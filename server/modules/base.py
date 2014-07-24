__author__ = 'Andrean'


class BaseServerModule(object):
    '''
    Base class for lemon server components.
    Everyone hase Core instance ref
    '''
    def __init__(self, core):
        self.__core = core
        self.__logger = None
        self.Name = "Base"

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError