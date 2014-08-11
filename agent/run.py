__author__ = 'Andrean'

import config
import traceback, sys

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
    except:
        traceback.print_exc(file=sys.stderr)
