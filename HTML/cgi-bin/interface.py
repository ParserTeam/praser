import cgi
from Controler import Controller
#from XmlModule import ConfigModule



#test = ConfigModule()

# Create instance of FieldStorage

form = cgi.FieldStorage()


def get_input_inf():
    # Get data from fields
    if form.getvalue('comment'):
        comment = form.getvalue('comment')
        return comment
    else:
        comment = "Nothing wos entered"
        return comment



controller = Controller()
text =  controller.check_text(get_input_inf())


# output = ['new inf']

def output_inf(output):
    print("Content-type:text/html\r\n\r\n")
    print()
    print("<html>")
    print("<head>")
    print("<TITLE>ERRORS PARSER</TITLE>")
    print("</head>")
    print("<BODY STYLE = 'color: #000080' 'background-color: #3366CC'>")
    print("<H1 STYLE = 'text-align: center'><STRONG>BSC ERRORS PARSER</STRONG></H1>")
    print("<TABLE>")
    print("<TBODY>")
    print("<DIV STYLE = 'text-align: center' 'height = 100%' >")
    print("<TR>")
    print("<form name='pars'>")
    print("<p STYLE = 'text-align: center'>Paste your log file here<Br>")
    print("<textarea name='comment' cols='200' rows='15'></textarea></p>")
    print(
        "<p><input name = 'inf' type='submit' value='Pars' formaction = '/cgi-bin/interface.py' formmethod = 'post' ></input><input type='reset' value='Clean'></p>")
    print("<p STYLE = 'text-align: center' >Errors:</p>")
    print("</form>")
    print(output)
    print("</TR>")
    print("</DIV>")
    print("</TBODY>")
    print("<TFOOT>")
    print("<TR>")
    print("<TD>")
    print("<ADDRESS> HERE WILL BE CONTAKT INFORMATION</ADDRESS>")
    print("</TD>")
    print("</TR>")
    print("</TFOOT>")
    print("</TABLE>")
    print("</body>")
    print("</html>")


output_inf(text)
