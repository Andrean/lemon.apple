__author__ = 'Andrean'

import core
import config
import modules.storage

if __name__ == "__main__":
    cfg = config.Config()
    cfg.Load('conf/server.yaml')
    cfg.LoadLogging('conf/logging.yaml')

    c = core.Core(cfg)
    c.add(modules.storage.Storage)
    print(core.Instance)
    print(c.Storage)

