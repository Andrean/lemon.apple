__author__ = 'Andrean'

import logging
from urllib.parse import urlsplit
from urllib.parse import parse_qs
import json
import types
import re
import traceback
import sys
import controllers.base as BaseController

#####################################################################################
#    Routes for routing agent's requests
#####################################################################################
AGENT_INTERFACE_ROUTES  = []

#####################################################################################
#    Routes for routing request from WEB-Server as web-interface
#####################################################################################
WEB_INTERFACE_ROUTES = []

#####################################################################################
#   Functions for make request and response references
#####################################################################################
def MakeRequest(requestHandler, path):
    requestHandler.query = parse_qs((urlsplit(path)).query)
    return requestHandler

def MakeResponse(requestHandler):
    def send_content(self, content, headers={}, code=200):
        self.send_response(code)
        self.send_header('Content-Type','text/plain;charset=utf-8')
        self.send_header('Content-Length',len(content))
        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(bytes(content, 'utf-8'))
    def send_json(self, content, headers={}, code=200):
        self.send_content( json.dumps(content), headers, code )
    requestHandler.send_content = types.MethodType( send_content, requestHandler )
    requestHandler.send_json    = types.MethodType( send_json, requestHandler )
    return requestHandler
#####################################################################################


class Router(object):
    def __init__(self, name):
        self.Name = name
        self.Methods = ['GET', 'POST', 'PUT', 'HEAD']
        self._logger = logging.getLogger('main.'+self.Name)
        self._routes = []
        self._handler = {}

    def install_handler(self, request_handler, method = 'GET'):
        self._handler = request_handler
        self._method = method

    def dispatch(self, path):
        try:
            for rule in self._routes:
                if rule['method'] == self._method and re.search(rule['pattern'], path):
                        rule['action'](
                        MakeRequest(self._handler, path),
                        MakeResponse(self._handler)
                    )
                return
        except:
            self._logger.error('{0}\n{1}'.format(self.name, ''.join(traceback.format_exception(*(sys.exc_info())))))
            # HTTP 500 Handler
            BaseController.get_500(MakeRequest(self._handler, path), MakeResponse(self._handler))


    def add_route(self, method, url_pattern, action):
        self._routes.append( {'pattern': url_pattern, 'action': action, 'method': method} )

    def load(self, routes):
        self._logger.debug('Loading routes')
        for rule in routes:
            try:
                self.add_route(*rule)
            except Exception as e:
                self._logger.exception(e)
        # after them load plugins routes
        # after all routes add rule HTTP 404 for .* path
        for method in self.Methods:
            self.add_route(method, r'.*', BaseController.get_404)

class AgentRouter(Router):
    def __init__(self):
        super().__init__('AGENT ROUTER')

    def load(self):
        super().load(AGENT_INTERFACE_ROUTES)


class WebRouter(Router):
    def __init__(self):
        super().__init__('WEB ROUTER')

    def load(self):
        super().load(WEB_INTERFACE_ROUTES)