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
def get_input_inf():
	# Get data from fields
	if form.getvalue('comment'):
		comment = form.getvalue('comment')
		return comment
	else:
		comment = "Not entered"
		return comment
#get_input_inf()

def output_inf(output):
	print("Content-type:text/html\r\n\r\n")
	print()
	print("<html>")
	print("<head>")
	print("<title>Text Area - Fifth CGI Program</title>")
	print("</head>")
	print("<body>")
	print(output)
	print("</body>")
	print("</html>")
output_inf(output)
		#return comment
print("Content-type:text/html\r\n\r\n")
print()
print("<html>")
print("<head>")
print("<title>Text Area - Fifth CGI Program</title>")
print("</head>")
print("<body>")
print(get_input_inf())
print("</body>")
print("</html>")
