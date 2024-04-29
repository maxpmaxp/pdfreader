import logging
log = logging.getLogger(__name__)

from io import BytesIO

from bitarray import bitarray
from PIL import Image

from .types.native import Array, Stream, HexString


class PILImageMixin(object):

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
            # Decode attr is optional
            values.append(self.Decode[index] if self.Decode else index)
        return values

    @staticmethod
    def get_pil_colorspace(pdf_cs):
        if isinstance(pdf_cs, Array) and pdf_cs[0] == "ICCBased":
            # We don't support ICCBased color spaces that's why we use number of color components
            # to determine the alternate one
            icc_profile = pdf_cs[1]
            if icc_profile.N == 1:
                pdf_cs = "DeviceGrey"
            elif icc_profile.N == 3:
                pdf_cs = "DeviceRGB"
            elif icc_profile.N == 4:
                pdf_cs = "DeviceCMYK"
            else:
                raise ValueError("Unexpected number of color components {}".format(icc_profile.N))

        if pdf_cs in ('DeviceRGB', 'RGB', 'CalRGB'):
            mode = "RGB"
        elif pdf_cs in ('DeviceCMYK', 'CMYK', 'CalCMYK'):
            mode = "CMYK"
        elif pdf_cs in ('DeviceGrey', 'G', 'CalGrey'):
            mode = "L"
        else:
            mode = "P"
        return mode

    def to_Pillow(self):
        """ Converts image into PIL.Image object.

            :return:  PIL.Image instance
        """
        size = self.Width, self.Height
        filter = self.Filter
        if isinstance(self.Filter, Array):
            filter = self.Filter[-1]

        if filter in ('DCTDecode', 'JPXDecode'):
            img = Image.open(BytesIO(self.stream))
        elif filter == 'CCITTFaxDecode' or self.ImageMask:
            img = Image.frombytes("1", size, bitarray(self.decoded).tobytes())
        else:
            # FlateDecode and others
            if isinstance(self.ColorSpace, Array):
                cs = self.ColorSpace
                my_cs, base_cs, hival, lookup = cs[0], cs[1], cs[2], cs[3]

                if isinstance(lookup, Stream):
                    lookup = lookup.filtered
                elif isinstance(lookup, HexString):
                    lookup = lookup.to_bytes()

                if my_cs == 'Indexed':
                    img = Image.new("P", size)
                    img.putpalette(lookup, self.get_pil_colorspace(base_cs))
                    img.frombytes(self.filtered)
                else:
                    log.debug("Unexpected colorspace: {}".format(my_cs))
                    img = Image.frombytes(self.get_pil_colorspace(base_cs), size, self.data)
            else:
                cs = self.get_pil_colorspace(self.ColorSpace)
                raw = self._recover_broken_image_if_necessary(cs, size, bytes(self.filtered))
                img = Image.frombytes(cs, size, raw)

        return img

    def _recover_broken_image_if_necessary(self, cs, size, raw):
        n_pixels = size[0] * size[1]
        if cs == 'RGB':
            expected_size = n_pixels * 3
        elif cs == 'CMYK':
            expected_size = n_pixels * 4
        elif cs == 'L' or cs == 'P':
            expected_size = n_pixels
        else:
            raise "Unsupported image mode: {}".format(cs)

        n_bytes = len(raw)
        # Try to work around broken images
        if n_bytes > expected_size:
            log.debug("Too many bytes fir the image. Truncating.")
            raw = raw[:expected_size]
        elif n_bytes < expected_size:
            log.debug("not enough bytes for the image. Appending zeros.")
            raw += bytes(expected_size - len(raw))

        return raw