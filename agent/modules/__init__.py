__author__ = 'Andrean'

import logging

class BaseAgentModule(object):
    """
    Base module class for Agent Module
    """
    Name = "Base"

    def __init__(self, core):
        self._core = core
        self._logger = logging.getLogger('main.'+self.Name)
        self._config = core.Config.GetSection(self.Name.upper())

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError