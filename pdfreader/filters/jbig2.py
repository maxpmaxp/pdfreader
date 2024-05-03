import logging
log = logging.getLogger(__name__)

filter_names = ('JBIG2Decode',)


def decode(binary, params):
    log.warning("JBIG2 decoder is not implemented. It returns raw unfiltered data.")
    return binary
