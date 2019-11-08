from bitarray import bitarray
from PIL import Image

from ..filters import apply_filter


class ImageSaverMixin(object):

    @property
    def Filter(self):
        return self.dictionary.get('Filter') or self.dictionary.get('F')

    @property
    def Width(self):
        return self.dictionary.get('Width') or self.dictionary.get('W')

    @property
    def Height(self):
        return self.dictionary.get('Height') or self.dictionary.get('H')

    @property
    def ColorSpace(self):
        return self.dictionary.get('ColorSpace') or self.dictionary.get('CS')

    @property
    def BitsPerComponent(self):
        return self.dictionary.get('BitsPerComponent') or self.dictionary.get('BPC')

    @property
    def Decode(self):
        return self.dictionary.get('Decode') or self.dictionary.get('D')

    @property
    def DecodeParms(self):
        return self.dictionary.get('DecodeParms') or self.dictionary.get('DP')

    @property
    def Intent(self):
        return self.dictionary.get('Intent')

    @property
    def Interpolate(self):
        return self.dictionary.get('Interpolate') or self.dictionary.get('I')

    @property
    def filtered(self):
        binary = self.data
        if self.Filter:
            binary = apply_filter(self.Filter, binary, self.dictionary.get('DecodeParms'))
        return binary

    @property
    def decoded(self):
        stream = bitarray()
        stream.frombytes(self.filtered)
        values = []
        for i in range(0, len(stream), self.BitsPerComponent):
            component = stream[i:i + self.BitsPerComponent]
            component.reverse()
            component.fill()
            component.reverse()
            index = int.from_bytes(component.tobytes(), 'big')
            values.append(self.Decode[index])
        return values

    def save(self, file_obj):
        size = self.Width, self.Height
        if self.ColorSpace in ('DeviceRGB', 'RGB'):
            mode = "RGB"
        elif self.ColorSpace in ('DeviceCMYK', 'CMYK'):
            mode = "CMYK"
        elif self.ColorSpace in ('DeviceGrey', 'G'):
            mode = "L"
        else:
            mode = "P"

        if self.Filter == 'FlateDecode':
            img = Image.frombytes(mode, size, self.data)
            img.save(file_obj)
        elif self.Filter in ('DCTDecode', 'JPXDecode', 'CCITTFaxDecode'):
            file_obj.save(self.data)
        else:
            img = Image.frombytes(mode, size, bytes(self.decoded))
            img.save(file_obj)

