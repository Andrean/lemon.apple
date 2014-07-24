__author__ = 'Andrean'

from modules.base import BaseServerModule

class Server(BaseServerModule):

    def __init__(self, _core):
        super().__init__(_core, 'Server')
        self._logger.info("Created")