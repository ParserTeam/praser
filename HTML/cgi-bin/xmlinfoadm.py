import cgi, cgitb

# fullname = os.path.join(".\config", name)  # take name
# if os.path.isfile(fullname):

import os
def xmlinfo(): # use it to output and open config files, criate html page(action for button XML INFO)
	print '''
			<html>
	        <head>
	        <TITLE>PARSER</TITLE>
	        <link rel="stylesheet" type="text/css" href="/style.css"> 
	        </head>
			<body>
			<div id ="goback"><p>&nbsp</p><nav><a href="/admin.html">BACK TO PARSER</a></nav><p>&nbsp</p></div>
			<DIV id = 'navigationxml'>
			<div STYlE='width:40%; float:left; background:Lavender;clear: both;height:0px;'>
	'''
	names = os.listdir(".\config")
	i = 0

	for name in names:
		i +=1
		print "<nav><span>"+str(i)+" - "+"</span><a href=/config/" + name +">" + name + "</a></nav>"
	print '''</div>
	</div>
	
	'''
	print '''
			<div STYlE='width:48%; float:right; text-align:right;background:Lavender;clear: both;height:0px;padding-right:20px'>
			<form name='t2' method='post' id = 'ajax_form'>
			<input type='text' name='txt' >  <br/>
			<input type='submit' value='Add new release' formaction='releaseAdd.py' />
			<input type="reset" value="Clean"/>
			</form>
			<p>&nbsp</p>
			<form name='t2' method='post' id = 'ajax_form'>
			<input type='text' name='txtdel' >  <br/>
			<input type='submit' value='Delete release' formaction='releaseAdd.py' />
			<input type="reset" value="Clean"/>
			</form>
			</div>
		    </body>
	        </html>'''
output = xmlinfo()
