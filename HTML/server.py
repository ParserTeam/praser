# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Demo CGI Server
"""
try:
    import BaseHTTPServer
    import CGIHTTPServer
except ImportError:
    import http.server as BaseHTTPServer
    import http.server as CGIHTTPServer
import cgitb

cgitb.enable()  # This line enables CGI error reporting

server = BaseHTTPServer.HTTPServer
handler = CGIHTTPServer.CGIHTTPRequestHandler
# server_address = ("100.93.20.49", 8000)
# server_address = ("192.168.1.133", 8000)
server_address = ("", 8000)
handler.cgi_directories = ["/cgi-bin", "/wsgi"]

httpd = server(server_address, handler)
httpd.serve_forever()
