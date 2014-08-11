__author__ = 'Andrean'

from modules import BaseAgentModule
import http.client
import defs.errors
from queue import Queue, Empty, Full
import threading

ClientLock = threading.Lock()

class Client(BaseAgentModule):

    Name = "Client"
    PackageSize = 4

    def __init__(self, core):
        super().__init__(core)
        self._command_channel = None
        self._data_channel = None
        self._queue = Queue(50)
        self._data_queue = Queue(500)
        self._stop = threading.Event()
        self.command_processor = threading.Thread(
            target=self.process_commands,
            daemon=True,
            name="COMMAND PROCESSOR"
        )
        self.data_processor = threading.Thread(
            target=self.process_data,
            daemon=True,
            name="DATA PROCESSOR"
        )

    def start(self):
        endpoint = self._config.get('server')
        if endpoint is None:
            raise defs.errors.LemonConfigurationError("Parameter: {0} not found".format('server'))
        host, port = endpoint.split(':')
        self._command_channel = http.client.HTTPConnection(host, int(port), 30)
        self._data_channel = http.client.HTTPConnection(host, int(port), 30)
        self.command_processor.start()
        self.data_processor.start()

    def process_commands(self):
        while True:
            try:
                item = self._queue.get(timeout=30)
            except Empty:
                if self._stop.is_set():
                    break
        self._command_channel.close()
        self._logger.info("Command Channel stopped successfully")

    def process_data(self):
        while True:
            try:
                item = self._queue.get(timeout=30)
            except Empty:
                if self._stop.is_set():
                    break
        self._data_channel.close()
        self._logger.info("Data Channel stopped successfully")

    def stop(self):
        self._logger.info("Stopping HTTP Connections...")
        self._stop.set()
        self.data_processor.join(timeout=60)
        self.command_processor.join(timeout=60)
        if self.command_processor.is_alive():
            self._logger.warn('Command Channel thread is still alive. Try to kill them')
            raise RuntimeError
        if self.data_processor.is_alive():
            self._logger.warn('Data Channel thread is still alive. Try to kill them')
            raise RuntimeError
        self._logger.info('HTTP Client was stopped successfully')

    def send_command(self, command):
        self._queue.put(command)

    def send_data(self, data):
        self._data_queue.put(data, timeout=50)