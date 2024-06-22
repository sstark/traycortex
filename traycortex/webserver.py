
from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import partial
import json
import re
import io
import logging
import socket
import sys

MAX_UPLOAD_SIZE = 100000
log = logging.getLogger("paperd.webserver")

class WebAPI(BaseHTTPRequestHandler):

    def __init__(self, routeMap, *args, **kwargs):
        self.apiFuncs = routeMap
        self.urlsGET = {
            "/v1/areas/(.*)": self.getApiFunc("getArea"),
            "/v1/areas$": self.getApiFunc("getAreas"),
            "/v1/update": self.getApiFunc("update")
        }
        self.urlsPUT = {
            "/v1/areas/(.*)": self.getApiFunc("setArea")
        }
        super().__init__(*args, **kwargs)

    def unknownApiFunc(self):
        log.error("unknown API function requested")

    def getApiFunc(self, name):
        return self.apiFuncs.get(name, self.unknownApiFunc)

    def matchUrl(self, routes):
        # first return value is actual function to run
        # second return value "name" is set to first match group of the route
        for k in routes:
            m = re.match(k, self.path)
            if m:
                try:
                    name = m.group(1)
                except:
                    name = None
                return routes[k], name
        return (None, None)

    def do_GET(self):
        func, name = self.matchUrl(self.urlsGET)
        if func:
            if name:
                out = func(name)
            else:
                out = func()
            self.send_response(200)
        else:
            out = "not found"
            self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(out).encode("utf-8")))

    def do_PUT(self):
        func, name = self.matchUrl(self.urlsPUT)
        if func:
            content_length = int(self.headers['Content-Length'])
            if content_length > MAX_UPLOAD_SIZE:
                self.send_response(413)
                out = "too much data"
            else:
                # Without those two lines response time is slow for PUT.
                # Normally this should be handled by the handle_expect_100
                # method, but I could not get it to work.
                self.send_response(100);
                self.end_headers()
                post_data = self.rfile.read(min(content_length, MAX_UPLOAD_SIZE))
                log.info("%d bytes read" % len(post_data))
                ret = func(name, post_data)
                if ret:
                    self.send_response(404)
                    out = ret
                else:
                    self.send_response(200)
                    out = "ok"
        else:
            out = "not found"
            self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(out).encode("utf-8")))

    def log_message(self, format, *args):
        log.info(format, *args)

    def log_error(self, format, *args):
        log.error(format, *args)

class WebServer():
    def __init__(self, routeMap, address):
        requestHandler = partial(WebAPI, routeMap)
        try:
            self.server = HTTPServer(address, requestHandler)
        except socket.gaierror:
            log.exception("invalid listen address: %s", address)
            sys.exit(1)
        log.info("starting webserver (%s:%s)" % address)

    def run(self):
        self.server.serve_forever()
