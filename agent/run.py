__author__ = 'Andrean'

import config,core
import traceback, sys, threading, time
import modules.client, modules.storage, modules.manager

if __name__ == "__main__":
    # load config
    # load core
    # load modules for core
    # start core
    # use schelve for storage
    try:
        cfg = config.Config()
        cfg.Load('conf/agent.yaml')
        cfg.LoadLogging('conf/logging.yaml')
        c = core.Core(cfg)
        c.add(modules.storage.Storage)
        c.add(modules.client.Client)
        c.add(modules.manager.Manager)
        c.start()
        #c.Client.send_data()
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc(file=sys.stderr)
    finally:
        c.stop()
