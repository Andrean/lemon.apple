__author__ = 'Andrean'

import yaml
import logging
import logging.config
import os


class Config(object):
    '''
    Class keeps all configuration of lemon agent
    Has methods for loading configuration
    '''
    Storage = {}
    Client  = {}
    Manager = {}
    root    = {}

    def __init__(self, file = None):
        self.file = file
        self.loggingFile = None

    def Load(self, filePath = None):
        if filePath is not None:
            self.file = filePath
        self.root = yaml.load(open(self.file))
        self.Storage = self.root.get('storage', {})
        self.Client  = self.root.get('client', {})

    def LoadLogging(self, loggingFilePath):
        self.loggingFile = loggingFilePath
        file = yaml.load(open(self.loggingFile))
        for item in file['handlers'].values():
            if item.__contains__('filename'):
                os.makedirs(os.path.dirname(item['filename']), exist_ok = True)
        logging.config.dictConfig(file)

    def GetSection(self, name):
        return self.root.get(name, {})
