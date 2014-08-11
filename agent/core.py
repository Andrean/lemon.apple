__author__ = 'Andrean'

import logging
import modules

Instance = None

class Core(object):
    '''
    Core class. It keeps all working instances of Lemon agent
    '''
    Config = {}
    # core components
    modules = {}

    def __init__(self, config=None):
        self.Config = config
        self._logger = logging.getLogger('main.Core')
        global Instance  # user for global access for Core
        Instance = self

    def add(self, module):
        instance = module(self)
        assert isinstance(instance, modules.BaseAgentModule)
        self.modules[instance.Name] = instance

    def start(self):
        self._logger.info('Starting modules')
        for module in self.modules.values():
            self._logger.debug('Starting module {}'.format(module.Name))
            module.start()

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
