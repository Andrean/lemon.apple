__author__ = 'Andrean'

import pymongo
import pymongo.errors
from modules.base import BaseServerModule

class Storage(BaseServerModule):

    def __init__(self, _core):
        super().__init__(_core, 'Storage')
        self._logger.info("Created")
        self._client = None
        self._connection = None

    def start(self):
        self.connect()

    def connect(self):
        self._logger.debug("Connecting to database")
        database = self._config.get('database', {})
        uri = database.get("uri")
        host = database.get('host','localhost')
        port = database.get('port',27017)
        db = database.get('db')
        try:
            if uri is not None:
                self._client = pymongo.MongoClient(uri)
            else:
                self._client = pymongo.MongoClient(host, port)
        except pymongo.errors.ConnectionFailure as e:
            self._logger.error("Cannot connect to mongodb", e)
            return
        if db is None:
            self._logger.error('[config error] parameter "db" not found')
        try:
            self._connection = self._client[db]
        except pymongo.errors.InvalidName:
            self._logger.error("Invalid Database name {0}".format(db))
            return
        self._logger.info('Storage successfully connected to db "{0}"'.format(db))
        return True

    def stop(self):
        pass

    @property
    def connection(self):
        if self._client is not None and self._client.alive():
            return self._connection
        self._logger.info('Connection error to database. Try to reconnect')
        if self.connect():
            return self._connection
