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

    def stop(self):
        pass

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