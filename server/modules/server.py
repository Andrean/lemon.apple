__author__ = 'Andrean'

from modules.base import BaseServerModule
import router

######################################################################
#   Server
#   Run all registered Listeners
######################################################################
class Server(BaseServerModule):
    def __init__(self, _core):
        super().__init__(_core, 'Server')
        agent_router = router.AgentRouter()
        web_router = router.WebRouter()

        self.agent_listener = Listener(HTTPRequestHandler, agent_router)
        endpoint = self._config.get('agent_interface',{}).get('listenerEndpoint')
        address = endpoint.split(':')
        self.agent_listener.set_endpoint(tuple([address[0], int(address[1])]))

        self.web_listener = Listener(HTTPRequestHandler, web_router)
        endpoint = self._config.get('web_interface',{}).get('listenerEndpoint')
        address = endpoint.split(':')
        self.web_listener.set_endpoint(tuple([address[0], int(address[1])]))

        self._logger.info("Server initiated")

    def start(self):
        self.agent_listener.start()
        self._logger.info('Agent Listener started')
        self.web_listener.start()
        self._logger.info('Web Listener started')

    def stop(self):
        self.agent_listener.stop()
        self._logger.info('Agent Listener was stopped')
        self.web_listener.stop()
        self._logger.info('Web Listener was stopped')

######################################################################
#   HTTPListener
#   Class for listen and handle http requests
######################################################################
import http.server
from socketserver import ThreadingMixIn
import threading

SOCKET_TIMEOUT = 60


class ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    pass


class Listener(threading.Thread):
    def __init__(self, handler_class, router_instance):
        self._handler = handler_class
        self._router = router_instance
        self._httpd = None
        self._endpoint = None
        super().__init__()

    def run(self):
        self._router.load()
        self.listen()

    def set_endpoint(self, server_address):
        self._endpoint = server_address

    def listen(self):
        self._httpd = ThreadingHTTPServer(self._endpoint, self._handler)
        self._httpd.daemon_threads = True
        self._httpd.request_router = self._router
        self._httpd.serve_forever()

    def stop(self):
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.socket.close()

######################################################################
#   HTTPRequestHandler
#   Class for handling one request
######################################################################
class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.protocol_version = 'HTTP/1.1'
        super().__init__(request, client_address, server)

    def do_GET(self):
        router = self.server.request_router
        router.install_handler(self, 'GET')
        router.dispatch(self.path)

    def do_POST(self):
        router = self.server.request_router
        router.install_handler(self, 'POST')
        router.dispatch(self.path)