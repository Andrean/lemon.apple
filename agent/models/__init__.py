__author__ = 'Andrean'

import core
from bson.objectid import ObjectId


class BaseModel(object):
    """
    Base class for classes that use Storage for save themselfs
    """

    StorageName = "base"
    Instances = {}
    Core = core.Core

    def __init__(self, item=None):
        self._item = dict(id=ObjectId())
        if item is not None:
            self._item = item

    @property
    def _storage(self):
        return self.Core.Instance.Storage

    @property
    def _client(self):
        return self.Core.Instance.Client

    @classmethod
    def load_all(cls):
        items = cls._storage.get(cls.StorageName)
        if items is not None:
            for x in items:
                cls.Instances[x['id']] = cls(x)

    @classmethod
    def find(cls, _id):
        return cls.Instances.get(_id)

    def save(self):
        self.Instances[self.id] = self
        self._storage.set(self.StorageName, [x._item for x in self.Instances.values()])

    def delete(self):
        if self.id in self.Instances:
            self.Instances.pop(self.id)
            self._storage.set(self.StorageName, [x._item for x in self.Instances.values()])

    @property
    def id(self):
        return self._item.get('id')