__author__ = 'Andrean'

from modules import BaseAgentModule
import http.client
import defs.errors
from queue import Queue, Empty, Full
import threading
import re
import time
import json
import bson.json_util

ClientLock = threading.Lock()

def ParseBody(response):
    # get content type. If not found use default "text/plain" with encoding "utf-8"
    content_type = response.getheader('Content-Type','text/plain; charset=utf-8')
    # if Content-Length is not found - do not read body
    content_length = int(response.getheader('Content-Length', 0))
    match = re.match(r"([\w/-]+);\s*charset=([\w-]+)", content_type)
    content_charset = 'utf-8'
    if match:
        content_charset = match.group(2)
        content_type = match.group(1)
    body = response.read(content_length)
    if content_type == 'text/plain':
        response.text = str(body, content_charset)
        response.data = body
        return response
    if content_type == 'application/json':
        response.json = json.loads(str(body, content_charset), object_hook=bson.json_util.object_hook)
        return response
    if content_type == 'application/octet-stream':
        response.data = body
    return response

class Client(BaseAgentModule):

    Name = "Client"
    PackageSize = 4
    DefaultCharset='utf8'

    def __init__(self, core):
        super().__init__(core)
        self._command_channel = None
        self._data_channel = None
        self._queue = Queue(50)
        self._data_queue = Queue(500)
        self._stop = threading.Event()
        self.command_processor = threading.Thread(
            target=self.process_commands,
            name="COMMAND PROCESSOR"
        )
        self.data_processor = threading.Thread(
            target=self.process_data,
            name="DATA PROCESSOR"
        )

    def start(self):
        endpoint = self._config.get('server')
        if endpoint is None:
            raise defs.errors.LemonConfigurationError("Parameter: {0} not found".format('server'))
        host, port = endpoint.split(':')
        self._command_channel = http.client.HTTPConnection(host, int(port), 30)
        self._command_channel.name = 'Command Channel'
        self._command_channel.mutex = threading.Lock()
        self._data_channel = http.client.HTTPConnection(host, int(port), 30)
        self._data_channel.name = 'Data Channel'
        self._data_channel.mutex = threading.Lock()
        if self.connect_channel(self._command_channel) == 0:
            raise ConnectionError("Cannot connect Command Channel")
        if self.connect_channel(self._data_channel) == 0:
            raise ConnectionError("Cannot connect Data Channel")
        #self.command_processor.start()
        self.data_processor.start()

    def process_commands(self):
        while True:
            try:
                item = self._queue.get(timeout=10)
                response = self._request(channel=self._command_channel, url='/commands', **item)
                if response is not None:
                    print(response.status)
                    print(response.headers)
                    print(response.json)
                else:
                    self.connect_channel(self._command_channel)
                    self._logger.info('Clear Command Queue after reconnection')
                    with self._queue.mutex:
                        self._queue.queue.clear()
                self._queue.task_done()
            except Empty:
                if self._stop.is_set():
                    break
        self._command_channel.close()
        self._logger.info("Command Channel stopped successfully")

    def process_data(self):
        while True:
            try:
                item = self._data_queue.get(timeout=10)
                print(item)
                response = self._request(self._data_channel, 'POST', '/data', item)
                if response is not None:
                    pass
                    #check response status. it cannot be not 200
                    # todo: read answer of server and resend failed data items
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

    def send_commands(self, commands):
        with self._command_channel.mutex:
            response = self._request(self._command_channel, 'POST', '/commands', commands)
            if response is None:
                return None
            return response.json

    def send_data(self, data):
        self._data_queue.put(data, timeout=50)

    def get_commands(self):
        print(time.time())
        with self._command_channel.mutex:
            response = self._request(self._command_channel, 'GET', '/commands')
            if response is None:
                return None
            return response.json

    def _request(self, channel, method, url, obj=None):
        headers = dict()
        headers['Lemon-Agent-ID'] = str(self._core.Storage.agent_id)
        body = None
        try:
            if obj is not None:
                body = bytes(json.dumps(obj, default=bson.json_util.default), self.DefaultCharset)
                headers['Content-Length'] = len(body)
                headers['Content-Type'] = 'application/json; charset={0}'.format(self.DefaultCharset)
            channel.request(method, url, body, headers)
            res = channel.getresponse()
            return ParseBody(res)
        except ConnectionError as err:
            self._logger.exception(err)
            self.connect_channel(channel)
        except http.client.HTTPException as err:
            self._logger.exception(err)
            self.connect_channel(channel)
        return None

    def connect_channel(self, channel):
        self._logger.info('Connecting channel "{0}"...'.format(channel.name))
        attempts = 100
        while attempts > 0:
            self._logger.debug('Reconnection attempt: {0}'.format(100 -attempts))
            try:
                channel.close()
                channel.connect()
                break
            except Exception as e:
                self._logger.exception(e)
                attempts -= 1
                time.sleep(10)
        if attempts > 0:
            self._logger.info('Successfully connected to {0}({1}:{2})'.format(channel.name, channel.host, channel.port))
        return attempts

