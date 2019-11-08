import logging

from io import BytesIO

from bitarray import bitarray
from PIL import Image

from ..types import Array


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

    def get_pil_colorspace(self, pdf_cs):
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
                my_cs, base_cs, hival, lookup = cs[0], cs[1], cs[2], cs[3].filtered

                if my_cs == 'Indexed':
                    img = Image.new("P", size)
                    img.putpalette(lookup, self.get_pil_colorspace(base_cs))
                    img.frombytes(self.filtered)
                else:
                    logging.debug("Unexpected colorspace: {}".format(my_cs))
                    img = Image.frombytes(self.get_pil_colorspace(base_cs), size, self.data)
            else:
                cs = self.get_pil_colorspace(self.ColorSpace)
                img = Image.frombytes(cs, size, bytes(self.filtered))
        return img


# if __name__ == '__main__':
#
#     import pkg_resources
#     from pdfreader import PDFDocument
#     fd = pkg_resources.resource_stream('pdfreader', 'samples/billerica-pd-logs.pdf')
#     doc = PDFDocument(fd)
#     page = next(doc.pages())
#     img = page.Resources['XObject']['img0']
#     pil_img = img.to_Pillow()
#     pil_img.save("pd-logo.png")
#
#
#     fd = pkg_resources.resource_stream('pdfreader', 'samples/tyler-or-inline-image.pdf')
#     doc = PDFDocument(fd)
#     pages = [p for p in doc.pages()]
#     page = pages[7]
#     img = next(page.inline_images())
#     pil_img = img.to_Pillow()
#     pil_img.save("fax.png")
#
#     import pkg_resources
#     fd = pkg_resources.resource_stream('pdfreader', 'samples/waltham-pd-logs.pdf')
#     from pdfreader import PDFDocument
#     doc = PDFDocument(fd)
#     images = [i for i in doc.images()]
#     for i, img in enumerate(images):
#         img.to_Pillow().save("xobj-{}.png".format(i))
#
#     images = [i for i in doc.inline_images()]
#     for i, img in enumerate(images):
#         img.to_Pillow().save("inline-{}.png".format(i))

