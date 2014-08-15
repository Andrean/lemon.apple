__author__ = 'Andrean'

import time

def test(req):
    print('Command "test" is started')
    req.set_pending({'percent': 10,'msg': 'Progress began'})
    time.sleep(5)
    req.set_pending({'percent': 40,'msg': 'Progressing'})
    time.sleep(5)
    req.set_completed('Command "test" completed')

def test2(req):
    print('Command "test2" is started')
    req.set_pending({'percent': 10, 'msg': 'Progress began'})
    time.sleep(5)
    req.set_pending({'percent': 50, 'msg': 'Progressing'})
    time.sleep(5)
    req.set_pending({'percent': 80, 'msg': 'Progressing'})
    time.sleep(5)
    req.set_completed('Command "test2" completed')

def emulate_error(req):
    print("Command 'error' is started")
    req.set_pending({'percent': 10, 'msg': 'Progress began'})
    time.sleep(3)
    raise ValueError("Emulator error")