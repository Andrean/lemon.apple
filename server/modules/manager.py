__author__ = 'Andrean'

from modules.base import BaseServerModule
import core
import models.components

class Manager(BaseServerModule):

    def __init__(self, _core):
        super().__init__(_core, 'Manager')
        self._storage= None

    def start(self):
        self._storage = core.Instance.Storage

    def stop(self):
        pass

    @property
    def agents(self):
        conn = self._storage.connection
        for k in conn[models.components.Agent.Collection].find({}):
            yield models.components.Agent(k)
