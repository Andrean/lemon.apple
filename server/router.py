__author__ = 'Andrean'

import logging
import defs.errors as errors
from urllib.parse import urlsplit
from urllib.parse import parse_qs
import pymongo.errors
import json
import bson.json_util
import types
import re
import traceback
import sys
import controllers.base as BaseController
import controllers.agent_controller as agentsController
import controllers.web  as webController

#####################################################################################
#    Routes for routing agent's requests
#####################################################################################
AGENT_INTERFACE_ROUTES = [
    [   'GET',    r'^/commands$', agentsController.commands['get']      ],
    [   'POST',   r'^/commands$', agentsController.commands['post']     ],
]

#####################################################################################
#    Routes for routing request from WEB-Server as web-interface
#####################################################################################
WEB_INTERFACE_ROUTES = [
    [   'GET',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['get_entities']],
    [   'PUT',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['add_entity']  ],
    [   'POST',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['modify_entity']  ],
    [   'DELETE',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['del_entity']  ],
    [   'GET',  r'^/agents[?=%&_\-\+\w,\.]*$', webController.agent_manager['get_agents']  ],
    [   'GET',  r'^/contractors[?=%&_\-\+\w\.,]*$', webController.contractors.get ],
    [   'POST',  r'^/contractors$', webController.contractors.add                ]
]

#####################################################################################
#   Functions for make request and response references
#####################################################################################
def MakeRequest(requestHandler, path):
    requestHandler.query = parse_qs((urlsplit(path)).query)
    return requestHandler

def send_content(self, content, code=200, headers={}):
    self.send_response(code)
    if 'Content-Type' not in headers.keys():
        self.send_header('Content-Type', 'text/plain;charset=utf-8')
    if 'Content-Length' not in headers.keys():
        self.send_header('Content-Length', len(content))
    for header, value in headers.items():
        self.send_header(header, value)
    self.end_headers()
    self.wfile.write(bytes(content, 'utf-8'))

def send_json(self, content, code=200, headers={}):
    if 'Content_Type' not in headers.keys():
        headers['Content-Type'] = 'application/json; charset=utf8'
    self.send_content( json.dumps(content, default=bson.json_util.default), code, headers )

def MakeResponse(requestHandler):
    requestHandler.send_content = types.MethodType( send_content, requestHandler )
    requestHandler.send_json    = types.MethodType( send_json, requestHandler )
    requestHandler.data = None
    requestHandler.text = None
    requestHandler.json = None
    requestHandler = ParseBody(requestHandler)
    return requestHandler

def ParseBody(req):
    # get content type. If not found use default "text/plain" with encoding "utf-8"
    content_type = req.headers.get('Content-Type','text/plain; charset=utf-8')
    # if Content-Length is not found - do not read body
    content_length = int(req.headers.get('Content-Length', 0))
    match = re.match(r"([\w/-]+);\s*charset=([\w-]+)", content_type)
    content_charset = 'utf-8'
    if match:
        content_charset = match.group(2)
        content_type = match.group(1)
    body = req.rfile.read(content_length)
    if content_type == 'text/plain':
        req.text = str(body, content_charset)
        req.data = body
        return req
    if content_type == 'application/json':
        req.json = json.loads(str(body, content_charset), object_hook=bson.json_util.object_hook)
        return req
    if content_type == 'application/octet-stream':
        req.data = body
    return req



#####################################################################################


class Router(object):
    def __init__(self, name):
        self.Name = name
        self.Methods = ['GET', 'POST', 'PUT', 'HEAD', 'DELETE']
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
        except errors.BaseLemonException as e:
            self._logger.exception(e)
            self._handler.send_content = types.MethodType( send_content, self._handler )
            self._handler.send_json    = types.MethodType( send_json, self._handler )
            self._handler.send_json({'error': e.message})
        except pymongo.errors.PyMongoError as e:
            self._logger.exception(e)
            self._handler.send_content = types.MethodType( send_content, self._handler )
            self._handler.send_json    = types.MethodType( send_json, self._handler )
            self._handler.send_json({'error': {'code': e.code, 'message':e.details['err']}})
        except:
            self._logger.error('{0}\n{1}'.format(self.Name, ''.join(traceback.format_exception(*(sys.exc_info())))))
            # HTTP 500 Handler
            BaseController.get_500(self._handler)


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