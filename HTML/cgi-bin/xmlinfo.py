import cgi, cgitb
import os
def xmlinfo():
	print '''
			<html>
	        <head>
	        <TITLE>ERRORS PARSER</TITLE>
	        <link rel="stylesheet" type="text/css" href="http://localhost:8000/style.css">
	        </head>
			<body>
	'''
	names = os.listdir(".\config")
	for name in names:
		fullname = os.path.join(".\config", name) # take name
		if os.path.isfile(fullname):
			print "<DIV id = 'navigationxml'><nav><a href=/config/" + name +">" + fullname + "</a></nav>"
	print '''
	<p>&nbsp</p>
	<nav><a href="http://localhost:8000/">BACK TO PARSER</a></nav>
	</div>
		    </body>
	        </html>
	
	'''
output = xmlinfo()
