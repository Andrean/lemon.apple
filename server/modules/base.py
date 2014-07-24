__author__ = 'Andrean'

import logging

class BaseServerModule(object):
    '''
    Base class for lemon server components.
    Everyone hase Core instance ref
    '''
    def __init__(self, core, name):
        self._core = core
        self._logger = logging.getLogger('main.'+name)
        self.Name = name

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError