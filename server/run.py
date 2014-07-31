__author__ = 'Andrean'

import core
import uuid
import config
import modules.storage
import modules.server
import modules.manager
import models.components
import time

if __name__ == "__main__":
    try:
        cfg = config.Config()
        cfg.Load('conf/server.yaml')
        cfg.LoadLogging('conf/logging.yaml')

        c = core.Core(cfg)
        c.add(modules.storage.Storage)
        c.add(modules.server.Server)
        c.add(modules.manager.Manager)
        c.start()
        #while True:
        time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        c.stop()


