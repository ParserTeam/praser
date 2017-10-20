import cgi, cgitb

# fullname = os.path.join(".\config", name)  # take name
# if os.path.isfile(fullname):

import os
def xmlinfo(): # use it to output and open config files, criate html page(action for button XML INFO)
	print '''
			<html>
	        <head>
	        <TITLE>PARSER</TITLE>
	        <link rel="stylesheet" type="text/css" href="http://localhost:8000/style.css"> 
	        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
			<script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.2.1.min.js"></script>

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
		names = os.listdir(".\config")
		if name == "versions.txt":
			print '''
			<form name='t2' method='post' id = 'ajax_form'>
			<input type='text' name='txt' >  <br/>
			<input type='submit' value='Add new release' id = 'btn2' formaction='releaseAdd.py' />
			<input type="reset" value="Clean"/>
			</form>
			<form name='t2' method='post' id = 'ajax_form'>
			<input type='text' name='txtdel' >  <br/>
			<input type='submit' value='Delete release' id = 'btn2' formaction='releaseAdd.py' />
			<input type="reset" value="Clean"/>
			</form>
				'''
	print '''
	</div>
<p id="results"></p>
		    </body>
	        </html>
	
	'''
output = xmlinfo()
