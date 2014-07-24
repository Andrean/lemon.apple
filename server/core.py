__author__ = 'Andrean'

Instance = None

class Core(object):
    '''
    Core class. It keeps all working instances of Lemon server
    '''
    Config = {}
    # core components
    Storage = None
    Server = None
    AgentManager = None
    PluginManager = None
    TaskManager = None

    def __init__(self, config = None):
        self.Config = config
        global Instance # user for global access for Core
        Instance = self