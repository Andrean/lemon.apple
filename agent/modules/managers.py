__author__ = 'Andrean'

from modules import BaseAgentModule
import bson.json_util
import datetime
import json
import threading
import traceback
import time
import commands
import os
import sys
import schedule
import subprocess
import defs.cmd
import queue
import core
import defs
import defs.scheduler
import hashlib

COMMANDS_POLL_INTERVAl = 5  # every 1 second try to get commands

class Manager(BaseAgentModule):

    Name = "Manager"

    def __init__(self, core):
        super().__init__(core)
        self._client = self._core.Client
        self._stop = threading.Event()
        self._commands_handler = None
        self.commandManager = None

    def start(self):
        self._logger.info('Starting commands timer')
        self._commands_handler = threading.Thread(target=self._handle_commands)
        self.commandManager = commands.CommandManager()
        self.commandManager.start()
        self._commands_handler.start()

    def stop(self):
        self._logger.info('Stopping commands timer...')
        self._stop.set()
        self.commandManager.stop()

    def _handle_commands(self):
        while not self._stop.is_set():
            # say to client 'GET commands' request
            # and wait for response in queue
            if not self.commandManager.isAlive:
                time.sleep(1)
                continue
            try:
                cmds = self._client.get_commands()
                self.commandManager.handle(cmds)
                status = self.commandManager.status(1)
                if len(status) > 0:
                    response = self._client.send_commands(status)
                    if response is None:
                        self._logger.error("Server did not answered on 'send_commands'")
            except ValueError as e:
                self._logger.error('Unknown response from server: {0}'.format(e))
                time.sleep(1)
            except Exception as err:
                self._logger.exception(err)
                time.sleep(1)




