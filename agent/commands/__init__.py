__author__ = 'Andrean'

import defs.cmd
import threading
import traceback
import sys
import logging
import time
from commands.routes import Routes


class CommandManager(threading.Thread):

    def __init__(self):
        super().__init__()
        self.mutex = threading.Lock()
        self._stop_event = threading.Event()
        self.command_ready = threading.Event()
        self._new_commands = threading.Event()
        self._commands = []
        self.router = CommandRouter()

    def run(self):
        self.router.load(Routes)
        while not self._stop_event.is_set():
            self._new_commands.wait(1)
            if self._new_commands.is_set():
                with self.mutex:
                    for x in self._commands:
                        if x.status == defs.cmd.CommandStatusEnum.present:
                            CommandHandler(x, self)
                self._new_commands.clear()

    def status(self, timeout=None):
        self.command_ready.wait(timeout)
        with self.mutex:
            result = self._commands
            if self.command_ready.is_set():
                l = []
                for x in self._commands:
                    if x.status != defs.cmd.CommandStatusEnum.completed and x.status != defs.cmd.CommandStatusEnum.error:
                        l.append(x)
                self._commands = l
                self.command_ready.clear()
            return [x.to_dict() for x in result]

    def handle(self, commands):
        if type(commands) == list:
            if len(commands) > 0:
                with self.mutex:
                    self._commands.extend([defs.cmd.Command(x) for x in commands])
                    self._new_commands.set()
        else:
            raise ValueError("Unknown type of commands")

    def stop(self):
        self._stop_event.set()


class CommandHandler(object):
    def __init__(self, command_obj, manager):
        self.command = command_obj
        self.manager = manager
        self.router = self.manager.router
        t = threading.Thread(target=self.do, daemon=True)
        t.start()

    def do(self):
        self.router.dispatch(self, self.command.cmd)

    def set_status(self, status, msg):
        with self.manager.mutex:
            self.command.response = msg
            self.command.status = status

    def set_pending(self, msg=""):
        self.set_status(defs.cmd.CommandStatusEnum.pending, msg)

    def set_error(self, msg=""):
        self.set_status(defs.cmd.CommandStatusEnum.error, msg)
        self.manager.command_ready.set()

    def set_completed(self, msg=""):
        self.set_status(defs.cmd.CommandStatusEnum.completed, msg)
        self.manager.command_ready.set()

class CommandRouter(object):

    def __init__(self):
        self._logger = logging.getLogger('main.'+self.__class__.__name__)
        self._routes = []

    def dispatch(self, handler, command):
        try:
            for route in self._routes:
                if route[0] == command:
                    route[1](handler)
                    return
        except:
            handler.set_error(traceback.format_exception(*(sys.exc_info())))
            return
        handler.set_error('Unhandled command: {0}'.format(command))

    def load(self, routes):
        self._routes.extend(routes)







