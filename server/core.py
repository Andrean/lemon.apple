__author__ = 'Andrean'

from modules.base import BaseServerModule
# module variables
Instance = None


class Core(object):
    '''
    Core class. It keeps all working instances of Lemon server
    '''
    Config = {}
    # core components
    modules = {}

    def __init__(self, config = None):
        self.Config = config
        global Instance # user for global access for Core
        Instance = self

    def add(self, module):
        instance = module(self)
        assert isinstance(instance, BaseServerModule)
        self.modules[instance.Name] = instance

    @property
    def Storage(self):
        return self.modules.get('Storage')
    @property
    def Server(self):
        return self.modules.get('Server')
