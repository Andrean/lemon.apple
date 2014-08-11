__author__ = 'Andrean'

import config, core
import traceback, sys
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
        print(c.Storage.get('agent_id'))
    except:
        traceback.print_exc(file=sys.stderr)
