__author__ = 'Andrean'

from threading import Thread, Event


class IntervalTimer(Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """

    def __init__(self, interval, function, iteration=-1, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.function = function
        self.iteration = iteration
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.iteration == 0 or self.finished.is_set():
                break
            self.function(*self.args, **self.kwargs)
            if self.iteration > 0:
                self.iteration -= 1