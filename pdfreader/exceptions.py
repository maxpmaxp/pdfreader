

class ParserException(Exception):
    pass


class TokenNotFound(ParserException):
    pass


class EOFException(Exception):
    pass