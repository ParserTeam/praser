import cgi
form = cgi.FieldStorage()

def add_button():
    print """
    <p><b>Key</b></br>
    <input type ="text" size="40">
    <input type = "submit" a>
    </p>"""





print "Content-type:text/html\r\n\r\n"
print """
    <html>
    <head>
    <TITLE>Add new xml config</TITLE>
    </head>
    <BODY STYLE = 'color: #000080' 'background-color: #3366CC'>
    <H1 STYLE = 'text-align: center'><STRONG>ADD NEW XML CONFIG</STRONG></H1>
    <TABLE>
    <TBODY>
    <DIV STYLE = 'text-align: center' 'height = 100%' >
    <TR>
    <form name = "test" method = "post">
    <p><b>Key</b></br>
    <input type ="text" size="50">        
    </p>
    <p><b>Key</b></br>
    <input type ="text" size="20">        
    </p>
    </from>
    </TR>
    </DIV>
    </TBODY>
    <TFOOT>
    <TR>
    <TD>
    </TD>
    </TR>
    </TFOOT>
    </TABLE>
    </body>
    </html>"""





def get_input_inf():
    # Get data from fields
    if form.getvalue('comment'):
        comment = form.getvalue('comment')
        return comment
    else:
        comment = "Nothing wos entered"
        return comment

# def output_inf(output):
#     print "Content-type:text/html\r\n\r\n"
#     print """
#         <html>
#         <head>
#         <TITLE>ERRORS PARSER</TITLE>
#         </head>
#         <BODY STYLE = 'color: #000080' 'background-color: #3366CC'>
#         <H1 STYLE = 'text-align: center'><STRONG>BSC ERRORS PARSER</STRONG></H1>
#         <TABLE>
#         <TBODY>
#         <DIV STYLE = 'text-align: center' 'height = 100%' >
#         <TR>
#         <form name='pars'>
#         <p STYLE = 'text-align: center'>Paste your log file here<Br>
#         <textarea name='comment' cols='200' rows='15'></textarea></p>
#         <p><input name = 'inf' type='submit' value='Pars' formaction = '/cgi-bin/interface.py' formmethod = 'post' ></input><input type='reset' value='Clean'>
#         <input name = 'add_xml' type = 'submit' value = 'Add new config' formaction = '/cgi-bin/AddXmlConfig.py' >
#         </p>
#         <p STYLE = 'text-align: center' >Errors:</p>
#         </form>
#         {}
#         </TR>
#         </DIV>
#         </TBODY>
#         <TFOOT>
#         <TR>
#         <TD>
#         <ADDRESS> HERE WILL BE CONTAKT INFORMATION</ADDRESS>
#         </TD>
#         </TR>
#         </TFOOT>
#         </TABLE>
#         </body>
#         </html>""".format(output)

#
# output_inf("sdasdklasldjaskl")
