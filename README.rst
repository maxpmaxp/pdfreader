# pdfreader

*pdfreader* is a Pythonic API for:
    * extracting texts, images and other data from PDF documents
    * accessing different objects within PDF document


*pdfreader* is **NOT** a tool:
    * to create or update PDF files
    * to split PDF files into pages or other pieces
    * convert PDFs to any other format


**Warning**: *pdfreader* supports **Python 3 only**.

## Features:

  * Python 3.6+
  * Follows `PDF-1.7 <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf>`
  * Lazy objects access allows to process huge PDF documents quite fast
  * Allows to extract texts (pure strings and formatted text objects)
  * Allows to extract PDF forms data (pure strings and formatted text objects)
  * Allows to extract images and image masks as `Pillow/PIL Images <https://pillow.readthedocs.io/en/stable/reference/Image.html>`
    without loosing the quality
  * Supports all PDF encodings, CMap, predefined cmaps.
  * Allows to access any document objects and resources and extract the data you need
    (fonts, annotations, metadata, multimedia, etc.)

## Tutorial and Documentation

Tutorial, real-life examples and documentation <......>

## Related Projects

  * `pdfminer <https://github.com/euske/pdfminer>` (cool stuff)
  * `pyPdf <http://pybrary.net/pyPdf/>`
  * `xpdf <http://www.foolabs.com/xpdf/>`
  * `pdfbox <http://pdfbox.apache.org/>`
  * `mupdf <http://mupdf.com/>`

## References
  * `Document management - Potable document format <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf>`
  * `Adobe CMap and CIDFont Files Specification <https://www.adobe.com/content/dam/acom/en/devnet/font/pdfs/5014.CIDFont_Spec.pdf>`
  * `PostScript Language Reference Manual <https://www-cdf.fnal.gov/offline/PostScript/PLRM2.pdf>`
  * `Adobe CMap resources <https://github.com/adobe-type-tools/cmap-resources>`
  * `Adobe glyph list specification (AGL) <https://github.com/adobe-type-tools/agl-specification>`
