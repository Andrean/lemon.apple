__author__ = 'Andrean'


from threading import Thread, Event


class StoppableThread(Thread):

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
