__author__ = 'Andrean'

from modules.base import BaseServerModule

class Storage(BaseServerModule):

    def __init__(self, _core):
        super().__init__(_core, 'Storage')
        self._logger.info("Created")