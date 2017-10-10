# -*- coding: utf-8  -*-
import cgi, os
import cgitb;

cgitb.enable()
#from Controler import Controller

output = ['new inf']
#controller = Controller()


def get_input_inf():
    form = cgi.FieldStorage()
    # form = cgi.FieldStorage()
    # Get data from fields
    comment = form.getvalue('comment')
    if comment is not None:
        return comment
    # if form.getvalue('comment'):
    # print (comment)
    # print (output)
    else:
        return "Nothing wos entered"
        # comment = "Nothing wos entered"
        # return comment


# get_input_inf()

text = {'rxcap.xml': [{'MO': 'RXOTG-187', 'CASCADABLE': 'YES', 'OMLF1': {'F1': 'TRXC function change not supported by the BTS.', 'F2': 'Automatic ciphering capability not supported by the BTS.', 'F15': 'MCTR not supported by the BTS.', 'F22': 'MCTR maximum allowed power extension not supported by the BTS.', 'F25': 'Native IP Configuration not supported by the BTS.', 'F27': 'Reporting of Access Burst Info not supported by the BTS.', 'F28': 'Decimal resolution of configured power not supported by the BTS.'}, 'OMLF2': {}, 'RSLF1': {'F11': 'Extended CBCH not supported by the BTS.'}, 'RSLF2': 'FF', 'FTXADDR': 'NO'}]}


def get_file_up():
    form = cgi.FieldStorage()
    result = form.getvalue("filename")
    # result = form['filename'].value
    # f= open(result, 'r')
    # text = f.read()
    return result


# form = cgi.FieldStorage()
#
# # Get filename here.
# fileitem = form['filename']
#
# # Test if the file was uploaded
# if fileitem.filename:
# 	# strip leading path from file name to avoid
# 	# directory traversal attacks
# 	fn = os.path.basename(fileitem.filename)
# 	print fn
# 	#open('*/' + fn, 'wb').write(fileitem.file.read())
#
# 	message = 'The file "' + fn + '" was uploaded successfully'
#
# else:
# 	message = 'No file was uploaded'
#
# print message

# print "Content-Type: text/html; charset=utf-8"
# print
# form = cgi.FieldStorage()
# # print form
# if form.has_key("btn3"):
# 	print "Ok"
# 	print form['upfilename'].file.read()
# # fileitem = form.getvalue ('upfilename')
# # log_file = open(fileitem, 'r')
# # text = log_file.read()
# # print text
# # log_file.close()
# # # Test if the file was uploaded
# # if fileitem.upfilename:
# 	# strip leading path from file name to avoid
# 	# directory traversal attacks
# fn = os.path.basename(fileitem.upfilename)
# open('/tmp/' + fn, 'wb').write(fileitem.file.read())
# message = 'The file "' + fn + '" was uploaded successfully'
# print message
#
# else:
# message = 'No file was uploaded'

#
# print """\
# Content-Type: text/html\n
# <html>
# <body>
#    <p>%s</p>
# </body>
# </html>
# """ % (message,)
# print "Content-Type: text/html; charset=utf-8"
# print

# field = cgi.FieldStorage()
# if field.has_key("file_up"):
# 	print "Ok"
# 	print field['file_up'].value
# 	field['file_up'].file.read()

def output_inf(output):
    print "Content-type:text/html\r\n\r\n"
    print
    # print("<html>")
    # print("<head>")
    # print("<TITLE>ERRORS PARSER</TITLE>")
    # print("</head>")
    # print("<BODY STYLE = 'color: #000080' 'background-color: #3366CC'>")
    # print("<H1 STYLE = 'text-align: center'><STRONG>BSC ERRORS PARSER</STRONG></H1>")
    # print("<TABLE>")
    # print("<TBODY>")
    # print("<DIV STYLE = 'text-align: center' 'height = 100%' >")
    # print("<TR>")
    # print("<form name='pars'>")
    # print("<p STYLE = 'text-align: center'>Paste your log file here<Br>")
    # print("<textarea name='comment' cols='200%' rows='15'></textarea></p>")
    # print("<p><input name = 'inf' type='submit' value='Pars' formaction = '/cgi-bin/interface.py' formmethod = 'post'></input><input type='reset' value='Clean'></p>")
    # print("<p STYLE = 'text-align: center' >Errors:</p>")
    # print("</form>")
    # print output
    # print get_input_inf()
    # print get_file_up()
    # print(table_result())
    # print("</TR>")
    # print("</DIV>")
    # print("</TBODY>")
    # print("<TFOOT>")
    # print("<TR>")
    # print("<TD>")
    # print("<ADDRESS>HERE WILL BE CONTAKT INFORMATION</ADDRESS>")
    # print("</TD>")
    # print("</TR>")
    # print("</TFOOT>")
    # print("</TABLE>")
    # print("</body>")
    # print("</html>")
    a = output
    #print type(a)

    if len(a) != 0:
        print'''
			<link rel="stylesheet" type="text/css" href="style.css">
			<link rel='stylesheet prefetch' href='http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css'>
			<link rel='stylesheet prefetch' href='http://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.10.0/bootstrap-table.min.css'>
			<link rel='stylesheet prefetch' href='http://rawgit.com/vitalets/x-editable/master/dist/bootstrap3-editable/css/bootstrap-editable.css'>
			<div class="container">
			 <table class="table table-bordered">
		'''
        for i in a:
            print'''
								<tr>
										<th colspan="4" ></th>
								</tr>
							'''
            print'''
				<tr>
					<th colspan="4" >''' + i[:i.find(".")].upper() + '''</th>
				</tr>
			'''
            for j in a.get(i):
                b = j
                print '''
					<tr>
							<th colspan="4" ></th>
					</tr>
				'''
                for z in b:
                    if type(b.get(z)) != dict:
                        print '''
							<tr class="bg-primary">
							  <th>''' + z + ''' -''' + '''</th>
							  <th colspan="3" >''' + b.get(z) + ''' ;''' + '''</th>
							</tr>
						'''
                    else:
                        if len(b.get(z)) != 0:
                            print '''
								<tr class="bg-success ">
								  <th>''' + z + ''' :''' + '''</th>
								  <th colspan="3" >ERRORS:</th>
								</tr>
							'''
                            for y in b.get(z):
                                print '''
									<tr class="bg-success ">
									  <th>''' + y + ''' -''' + '''</th>
									  <th colspan="3" >''' + b.get(z).get(y) + ''' ;''' + '''</th>
									</tr>
								'''
                        else:
                            print '''
								<tr class="bg-success ">
								  <th>''' + z + ''' -''' + '''</th>
								  <th colspan="3" >OK;</th>
								</tr>
							'''
        print '''
					</table>
			</div>
				'''


# output_inf(output)

