__author__ = 'Andrean'

import core
import config
import modules.storage
import modules.server
import time

if __name__ == "__main__":
    cfg = config.Config()
    cfg.Load('conf/server.yaml')
    cfg.LoadLogging('conf/logging.yaml')

    c = core.Core(cfg)
    c.add(modules.storage.Storage)
    c.add(modules.server.Server)
    c.start()
    print(core.Instance)
    print(c.Storage)
    try:
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        c.stop()


