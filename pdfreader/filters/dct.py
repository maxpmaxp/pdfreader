from PIL import Image

filter_names = ('DCTDecode', 'DCT')


def decode(binary, *_):
    img = Image.frombytes(binary)
    return img.tobytes()
