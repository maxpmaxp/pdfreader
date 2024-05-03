import logging
log = logging.getLogger(__name__)

filter_names = ('JPXDecode',)


def decode(binary, params):
    log.warning("JPX decoder is not implemented. It returns raw unfiltered data.")
    return binary
