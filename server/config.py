__author__ = 'Andrean'

import os
import yaml
import logging.config

class Config(object):
    '''
    Class keeps all configuration of lemon server
    Has methods for loading configuration
    '''
    Storage = {}
    Server  = {}

    def __init__(self, file = None):
        self.file = file
        self.loggingFile = None

    def Load(self, filePath = None):
        if filePath is not None:
            self.file = filePath
        file = yaml.load(open(self.file))
        self.Storage = file.get('STORAGE', {})
        self.Server  = file.get('SERVER', {})

    def LoadLogging(self, loggingFilePath):
        self.loggingFile = loggingFilePath
        file = yaml.load(open(self.loggingFile))
        for item in file['handlers'].values():
            if item.__contains__('filename'):
                os.makedirs(os.path.dirname(item['filename']), exist_ok = True)
        logging.config.dictConfig(file)
