import cgi, cgitb

# fullname = os.path.join(".\config", name)  # take name
# if os.path.isfile(fullname):
import os
def xmlinfo(): # use it to output and open config files, criate html page(action for button XML INFO)
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
	i = 0
	for name in names:
		i +=1
		print "<nav><span>"+str(i)+" - "+"</span><a href=/config/" + name +">" + name + "</a></nav>"
	print '''
	</div>
		    </body>
	        </html>
	
	'''
output = xmlinfo()
