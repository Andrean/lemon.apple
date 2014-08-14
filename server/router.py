__author__ = 'Andrean'

import logging
from urllib.parse import urlsplit
from urllib.parse import parse_qs
import json
import types
import re
import traceback
import sys

import pymongo.errors
import bson.json_util

import defs.errors as errors
import controllers.base as BaseController
import routes.web_interface as web_interface
import routes.agent_interface as agent_interface

#####################################################################################
#   Functions for make request and response references
#####################################################################################
def MakeRequest(requestHandler, path):
    requestHandler.query = parse_qs((urlsplit(path)).query)
    return requestHandler

def send_content(self, content, code=200, headers={}):
    self.send_response(code)
    if not isinstance(content, str):
        content = str(content)
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

    def dispatch(self, handler, method, path):
        try:
            for rule in self._routes:
                if rule['method'] == method and re.search(rule['pattern'], path):
                    rule['action'](
                        MakeRequest(handler, path),
                        MakeResponse(handler)
                    )
                    return
        except errors.BaseLemonException as e:
            self._logger.exception(e)
            handler.send_content = types.MethodType( send_content, handler )
            handler.send_json    = types.MethodType( send_json, handler )
            handler.send_json({'error': e.message})
        except pymongo.errors.PyMongoError as e:
            self._logger.exception(e)
            handler.send_content = types.MethodType( send_content, handler )
            handler.send_json    = types.MethodType( send_json, handler )
            handler.send_json({'error': {'code': e.code, 'message':e.details['err']}})
        except:
            self._logger.error('{0}\n{1}'.format(self.Name, ''.join(traceback.format_exception(*(sys.exc_info())))))
            # HTTP 500 Handler
            BaseController.get_500(handler)


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
        super().load(agent_interface.ROUTES)


class WebRouter(Router):
    def __init__(self):
        super().__init__('WEB ROUTER')

    def load(self):
        super().load(web_interface.ROUTES)