#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
import cgi

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
if form.getvalue('comment'):
	comment = form.getvalue('comment')
else:
    comment = "Not entered"

#print("Content-type:text/html\r\n\r\n")
#print()
#print("<html>")
#print("<head>")
#print("<title>Text Area - Fifth CGI Program</title>")
#print("</head>")
#print("<body>")
#print(comment)
#print("</body>")
#print("</html>")

#new = ["efefe"]