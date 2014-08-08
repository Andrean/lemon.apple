__author__ = 'Andrean'


class BaseLemonException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class LemonException(BaseLemonException):
    pass


class LemonAttributeError(BaseLemonException, AttributeError):
    pass


class LemonValueError(BaseLemonException, ValueError):
    pass