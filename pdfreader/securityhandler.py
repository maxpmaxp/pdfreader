# Copied from https://github.com/euske/pdfminer/blob/df53c8ed539760b5318d9da5f23b14f7d158710a/pdfminer/pdfdocument.py
# and refactored

import struct

from hashlib import md5

from Crypto.Cipher import ARC4, AES
from Crypto.Hash import SHA256

from .types.native import HexString, Stream, String


def security_handler_factory(docid, encrypt, password=''):
    version = encrypt.get('V', 0)
    if version not in SECURITY_HANDLERS_BY_VERSION:
        raise ValueError("Unsupported security handler version: {}".format(version))
    return SECURITY_HANDLERS_BY_VERSION[version](docid, encrypt, password)


class StandardSecurityHandler(object):
    """ Standard security handler supporting versions 2 and 3

        :param docid: Array containing document ID. Comes in document's trailer.
        :param encrypt: 'Encrypt' dictionary containing encryption parameters. Comes in document's trailer.
        :param password: Password for encrypted PDF. Optional. Default ''.
    """

    #: contains first entry from document ID array
    docid = None
    #: 'Encrypt' dictionary containing encryption parameters
    encrypt = None
    #: document access password
    password = None

    PASSWORD_PADDING = b'(\xbfN^Nu\x8aAd\x00NV\xff\xfa\x01\x08..\x00\xb6\xd0h>\x80/\x0c\xa9\xfedSiz'
    supported_revisions = (2, 3)

    def __init__(self, docid, encrypt, password=''):
        self.docid = bytes(bytearray.fromhex(docid[0]))
        self.encrypt = encrypt
        self.password = password.encode("utf-8")
        self.init()
        return

    def init(self):
        self.init_params()
        if self.r not in self.supported_revisions:
            raise ValueError('Unsupported revision: param={}'.format(self.encrypt))
        self.init_key()
        return

    def init_params(self):
        self.v = self.encrypt.get('V', 0)
        self.r = self.encrypt['R']
        self.p = self.encrypt['P']
        self.o = self.encrypt['O']
        if isinstance(self.o, str):
            self.o = bytes(bytearray.fromhex(self.o))
        self.u = self.encrypt['U']
        if isinstance(self.u, str):
            self.u = bytes(bytearray.fromhex(self.u))
        self.length = self.encrypt.get('Length', 40)
        self.encrypt_metadata = True
        return

    def init_key(self):
        self.key = self.authenticate(self.password)
        if self.key is None:
            raise ValueError("Incorrect password")
        return

    def is_printable(self):
        return bool(self.p & 4)

    def is_modifiable(self):
        return bool(self.p & 8)

    def is_extractable(self):
        return bool(self.p & 16)

    def compute_u(self, key):
        if self.r == 2:
            # Algorithm 4: Computing the encryption dictionary's U (user password value). Revision 2.
            return ARC4.new(key).encrypt(self.PASSWORD_PADDING)  # b
        else:
            # self.r >= 3
            # Algorithm 5: Computing the encryption dictionary's U (user password value). Revision >=3.
            hash = md5(self.PASSWORD_PADDING)  # b
            hash.update(self.docid)  # c
            result = ARC4.new(key).encrypt(hash.digest())  # d
            for i in range(1, 20):  # e
                k = bytes((c ^ i) for c in key)
                result = ARC4.new(k).encrypt(result)
            result += b'\x00' * 16  # f
            return result

    def compute_encryption_key(self, password):
        # Algorithm 2: Computing an encryption key
        password = (password + self.PASSWORD_PADDING)[:32]  # a
        hash = md5(password)  # b
        hash.update(self.o)  # c
        hash.update(struct.pack('<l', self.p))  # d
        hash.update(self.docid)  # e
        if self.r >= 4:
            if not self.encrypt_metadata:
                hash.update(b'\xff\xff\xff\xff') # f
        result = hash.digest() # g
        if self.r >= 3: # h
            n = self.length // 8
            for _ in range(50):
                result = md5(result[:n]).digest()
        else:
            n = 5 # i
        return result[:n] # i

    def authenticate(self, password):
        key = self.authenticate_user_password(password)
        if key is None:
            key = self.authenticate_owner_password(password)
        return key

    def authenticate_user_password(self, password):
        key = self.compute_encryption_key(password)
        if self.verify_encryption_key(key):
            return key

    def verify_encryption_key(self, key):
        # Algorithm 3.6
        u = self.compute_u(key)
        if self.r == 2:
            return u == self.u
        return u[:16] == self.u[:16]

    def authenticate_owner_password(self, password):
        # Algorithm 3.7
        password = (password + self.PASSWORD_PADDING)[:32]
        hash = md5(password)
        if self.r >= 3:
            for _ in range(50):
                hash = md5(hash.digest())
        n = 5
        if self.r >= 3:
            n = self.length // 8
        key = hash.digest()[:n]
        if self.r == 2:
            user_password = ARC4.new(key).decrypt(self.o)
        else:
            user_password = self.o
            for i in range(19, -1, -1):
                k = bytes((c ^ i) for c in key)
                user_password = ARC4.new(k).decrypt(user_password)
        return self.authenticate_user_password(user_password)

    def decrypt(self, obj):
        """
        Decrypts indirect objects: String, HexString, Stream

        :param obj: object to decrypt
        :type obj: :class:`~pdfreader.types.native.IndirectObject`

        :return:  :class:`~pdfreader.types.native.IndirectObject` containing decrypted data.
        """
        if isinstance(obj.val, Stream):
            obj.val.stream = self.decrypt_rc4(obj.num, obj.gen, obj.val.stream)
            obj.val.dictionary["Length"] = len(obj.val.stream)
        elif isinstance(obj.val, String):
            obj = String(self.decrypt_rc4(obj.num, obj.gen, obj.val))
        elif isinstance(obj.val, HexString):
            # ToDo: clarify if we need to convert String to HexString here
            obj = String(self.decrypt_rc4(obj.num, obj.gen, obj.val.to_bytes))
        else:
            raise TypeError("Can't decrypt object of type {}".format(type(obj.val)))
        return obj

    def decrypt_rc4(self, num, gen, data):
        key = self.key + struct.pack('<L', num)[:3] + struct.pack('<L', gen)[:2]
        hash = md5(key)
        key = hash.digest()[:min(len(key), 16)]
        data = ARC4.new(key).decrypt(data)
        return data


class StandardSecurityHandlerV4(StandardSecurityHandler):
    """ Standard security handler supporting version 4

        :param docid: Array containing document ID. Comes in document's trailer.
        :param encrypt: 'Encrypt' dictionary containing encryption parameters. Comes in document's trailer.
        :param password: Password for encrypted PDF. Optional. Default ''.
    """

    #: contains first entry from document ID array
    docid = None
    #: 'Encrypt' dictionary containing encryption parameters
    encrypt = None
    #: document access password
    password = None

    supported_revisions = (4,)

    def init_params(self):
        super(StandardSecurityHandlerV4, self).init_params()
        self.length = 128
        self.cf = self.encrypt.get('CF')
        self.stmf = self.encrypt['StmF']
        self.strf = self.encrypt['StrF']
        self.encrypt_metadata = bool(self.encrypt.get('EncryptMetadata', True))
        self.cfm = {} # decryption methods
        for k, v in self.cf.items():
            f = self.get_cfm(v['CFM'])
            if f is None:
                raise ValueError('Unknown crypt filter method: Encrypt=%r' % self.encrypt)
            self.cfm[k] = f
        self.cfm['Identity'] = self.decrypt_identity
        if self.strf not in self.cfm:
            raise ValueError('StrF {} not listed on CF'.format(self.strf))
        if self.stmf not in self.cfm:
            raise ValueError('StmF {} not listed on CF'.format(self.stmf))

    def get_cfm(self, name):
        res = None
        if name == 'V2':
            res = self.decrypt_rc4
        elif name == 'AESV2':
            res = self.decrypt_aes128
        return res

    def decrypt(self, obj):
        """ Decrypts indirect objects: String, HexString, Stream

            :param obj: object to decrypt
            :type obj: :class:`~pdfreader.types.native.IndirectObject`

            :return:  :class:`~pdfreader.types.native.IndirectObject` containing decrypted data.
        """
        if isinstance(obj.val, Stream):
            if obj.val.Type != 'Metadata' or self.encrypt_metadata:
                # metadata remains unchanged if EncryptMetadata is false
                decryptor = self.cfm[self.stmf]
                obj.val.stream = decryptor(obj.num, obj.gen, obj.val.stream)
                obj.val.dictionary["Length"] = len(obj.val.stream)
        elif isinstance(obj.val, String):
            decryptor = self.cfm[self.strf]
            obj = String(decryptor(obj.num, obj.gen, obj.val))
        elif isinstance(obj.val, HexString):
            # ToDo: clarify if we need to convert String to HexString here
            decryptor = self.cfm[self.strf]
            obj = String(decryptor(obj.num, obj.gen, obj.val.to_bytes))
        else:
            raise TypeError("Can't decrypt object of type {}".format(type(obj.val)))
        return obj

    def decrypt_identity(self, objid, genno, data):
        return data

    def decrypt_aes128(self, objid, genno, data):
        key = self.key + struct.pack('<L', objid)[:3] + struct.pack('<L', genno)[:2] + b'sAlT'
        hash = md5(key)
        key = hash.digest()[:min(len(key), 16)]
        return AES.new(key, mode=AES.MODE_CBC, IV=data[:16]).decrypt(data[16:])


class StandardSecurityHandlerV5(StandardSecurityHandlerV4):
    """ Standard security handler supporting version 5

        :param docid: Array containing document ID. Comes in document's trailer.
        :param encrypt: 'Encrypt' dictionary containing encryption parameters. Comes in document's trailer.
        :param password: Password for encrypted PDF. Optional. Default ''.
    """

    #: contains first entry from document ID array
    docid = None
    #: 'Encrypt' dictionary containing encryption parameters
    encrypt = None
    #: document access password
    password = None

    supported_revisions = (5,)

    def init_params(self):
        super(StandardSecurityHandlerV5, self).init_params()
        self.length = 256
        self.oe = self.encrypt['OE']
        self.ue = self.encrypt['UE']
        self.o_hash = self.o[:32]
        self.o_validation_salt = self.o[32:40]
        self.o_key_salt = self.o[40:]
        self.u_hash = self.u[:32]
        self.u_validation_salt = self.u[32:40]
        self.u_key_salt = self.u[40:]

    def get_cfm(self, name):
        if name == 'AESV3':
            return self.decrypt_aes256

    def authenticate(self, password):
        password = password[:127]
        hash = SHA256.new(password)
        hash.update(self.o_validation_salt)
        hash.update(self.u)
        if hash.digest() == self.o_hash:
            hash = SHA256.new(password)
            hash.update(self.o_key_salt)
            hash.update(self.u)
            return AES.new(hash.digest(), mode=AES.MODE_CBC, IV=b'\x00' * 16).decrypt(self.oe)
        hash = SHA256.new(password)
        hash.update(self.u_validation_salt)
        if hash.digest() == self.u_hash:
            hash = SHA256.new(password)
            hash.update(self.u_key_salt)
            return AES.new(hash.digest(), mode=AES.MODE_CBC, IV=b'\x00' * 16).decrypt(self.ue)

    def decrypt(self, obj):
        """ Decrypts indirect objects: String, HexString, Stream

            :param obj: object to decrypt
            :type obj: :class:`~pdfreader.types.native.IndirectObject`

            :return:  :class:`~pdfreader.types.native.IndirectObject` containing decrypted data.
        """
        return super(StandardSecurityHandlerV5, self).decrypt(obj)

    def decrypt_aes256(self, objid, genno, data):
        return AES.new(self.key, mode=AES.MODE_CBC, IV=data[:16]).decrypt(data[16:])


SECURITY_HANDLERS_BY_VERSION = {
    1: StandardSecurityHandler,
    2: StandardSecurityHandler,
    3: StandardSecurityHandler,
    4: StandardSecurityHandlerV4,
    5: StandardSecurityHandlerV5
}