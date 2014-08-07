__author__ = 'Andrean'

from modules.base import BaseServerModule
import core
import uuid
import bson.objectid
import models.components
import defs.cmd
import datetime


class Manager(BaseServerModule):

    def __init__(self, _core):
        super().__init__(_core, 'Manager')
        self._storage = None
        self._agents = None
        self._entities = None

    def start(self):
        self._storage = core.Instance.Storage
        self.ensure_index()

    def stop(self):
        pass

    def ensure_index(self):
        self._logger.info('Start indexing of data')
        models.components.Agent.ensure_index_schema()
        models.components.Entity.ensure_index_schema()
        models.components.Contractor.ensure_index_schema()
        self._logger.info('Indexing is over')

    @property
    def agents(self):
        if models.components.Agent.Instances is None:
            models.components.Agent.load_instances()
        return models.components.Agent

    @property
    def entities(self):
        if models.components.Entity.Instances is None:
            models.components.Entity.load_instances()
        return models.components.Entity

    @property
    def contractors(self):
        # don't load all instances to memory
        return models.components.Contractor

    @property
    def data_items(self):
        return models.components.DataItem