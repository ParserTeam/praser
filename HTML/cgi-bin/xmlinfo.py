import cgi, cgitb

# fullname = os.path.join(".\config", name)  # take name
# if os.path.isfile(fullname):
import os
def xmlinfo():
	print '''
			<html>
	        <head>
	        <TITLE>ERRORS PARSER</TITLE>
	        <link rel="stylesheet" type="text/css" href="http://localhost:8000/style.css">
	        </head>
			<body>
			<div id ="goback"><p>&nbsp</p><nav><a href="http://localhost:8000/">BACK TO PARSER</a></nav><p>&nbsp</p></div>
			<DIV id = 'navigationxml'>
	'''
	names = os.listdir(".\config")
	for name in names:
		print "<nav><a href=/config/" + name +">" + name + "</a></nav>"
	print '''
	</div>
		    </body>
	        </html>
	
	'''
output = xmlinfo()
