__author__ = 'Andrean'

import logging
from modules import BaseAgentModule


class Core(object):
    '''
    Core class. It keeps all working instances of Lemon agent
    Core is Singleton
    '''
    Instance = None
    Config = {}
    # core components
    modules = {}

    def __new__(cls, *args, **kwargs):
        if cls.Instance is None:
            cls.Instance = super(Core, cls).__new__(cls)
        return cls.Instance

    def __init__(self, config=None):
        self.Config = config
        self._logger = logging.getLogger('main.Core')
        self._order = []

    def add(self, module):
        instance = module(self)
        assert isinstance(instance, BaseAgentModule)
        self.modules[instance.Name] = instance
        self._order.append(instance.Name)

    def start(self):
        self._logger.info('Starting modules')
        for module_name in self._order:
            self._logger.debug('Starting module {0}'.format(module_name))
            self.modules[module_name].start()

    def stop(self):
        self._logger.info('Stopping modules')
        for module in self.modules.values():
            self._logger.debug('Stopping module {}'.format(module.Name))
            module.stop()

    @property
    def Storage(self):
        return self.modules.get('Storage')

    @property
    def Client(self):
        return self.modules.get('Client')

    @property
    def Manager(self):
        return self.modules.get('Manager')