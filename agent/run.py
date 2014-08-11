__author__ = 'Andrean'

import config,core
import traceback, sys, threading
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
        import sched, datetime, time
        s = sched.scheduler()
        def func(a=0):
            print("{0} : {1}".format(datetime.datetime.now(),a))
            t = threading.Thread(target=lambda: time.sleep(5))
            t.start()
        s.enter(5, 1, func, (1,))
        s.enter(6, 1, func, (2,))
        s.enter(10,1, func, (3,))
        s.run()
    except:
        traceback.print_exc(file=sys.stderr)
    finally:
        c.stop()
