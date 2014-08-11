__author__ = 'Andrean'

from modules import BaseAgentModule
import os
import socket
import shelve
import uuid

class Storage(BaseAgentModule):

    Name = "Storage"

    def __init__(self, core):
        super().__init__(core)

    def start(self):
        self._logger.info('Load Database on {0}'.format(self._config['data_path']))
        data_path = self._config['data_path']
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with shelve.open(data_path, 'c') as db:
            if 'agent_id' not in db:
                self._logger.info("Storage File not found. Creating new on {0}".format(data_path))
                self._logger.info("Generating new AGENT ID")
                agent_id = uuid.uuid3(uuid.NAMESPACE_DNS, socket.getfqdn(socket.gethostname()))
                self._logger.info("AGENT ID is {0}".format(agent_id))
                db['agent_id'] = agent_id
        self._db = data_path
        self._logger.info("Database is loaded")

    def stop(self):
        self._logger.info('Stopped')

    def get(self, key):
        with shelve.open(self._db, 'r') as db:
            return db.get(key)

    def set(self, key, value):
        with shelve.open(self._db) as db:
            db[key] = value