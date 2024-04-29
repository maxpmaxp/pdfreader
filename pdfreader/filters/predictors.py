import logging
log = logging.getLogger(__name__)

def _remove_predictors(data, predictor=None, columns=None):
    """ Remove LZW/Flate predictors
    1 - No prediction
    2 - TIFF predictor 2
    10 - PNG None
    11 - PNG Sub
    12 - PNG Up
    13 - PNG Average
    14 - PNG Paeth
    15 - PNG Optimum
    """
    if predictor is None:
        predictor = 1

    if predictor == 1:
        res = data
    elif predictor == 2:
        raise ValueError("TIFF prediction not implemented")
    elif 10 <= predictor <= 15:
        row_size = columns + 1
        res = b''
        for i in range(0, len(data), row_size):
            if data[i] + 10 != predictor:
                log.debug("Unexpected predictor {} in row {}. Expected value {}, columns {}"
                          .format(data[0] + 10, i, predictor, columns))
            res += data[i + 1:i + row_size]  # skip leading predictor byte

    else:
        raise ValueError("Unknown predictor type {}".format(predictor))
    return res
