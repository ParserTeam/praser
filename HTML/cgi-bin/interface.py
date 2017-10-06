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
text = controller.check_text(get_input_inf())

# output = ['new inf']

def output_inf(output):
    print("Content-type:text/html\r\n\r\n")
    print("""
        <html>
        <head>
        <TITLE>ERRORS PARSER</TITLE>
        </head>
        <BODY STYLE = 'color: #000080' 'background-color: #3366CC'>
        <H1 STYLE = 'text-align: center'><STRONG>BSC ERRORS PARSER</STRONG></H1>
        <TABLE>
        <TBODY>
        <DIV STYLE = 'text-align: center' 'height = 100%' >
        <TR>
        <form name='pars'>
        <p STYLE = 'text-align: center'>Paste your log file here<Br>
        <textarea name='comment' cols='200' rows='15'></textarea></p>
        <p><input name = 'inf' type='submit' value='Pars' formaction = '/cgi-bin/interface.py' formmethod = 'post' ></input><input type='reset' value='Clean'></p>
        <p STYLE = 'text-align: center' >Errors:</p>
        </form>
        {}
        </TR>
        </DIV>
        </TBODY>
        <TFOOT>
        <TR>
        <TD>
        <ADDRESS> HERE WILL BE CONTAKT INFORMATION</ADDRESS>
        </TD>
        </TR>
        </TFOOT>
        </TABLE>
        </body>
        </html>""".format(output))

    a = output

    for i in a:
        print(i[:i.find(".")] + "<p></p>")
        for j in a.get(i):
            if type(a.get(i).get(j)) != dict:
                print(j)
                print(a.get(i).get(j) + "<p></p>")
            else:
                if len(a.get(i).get(j)) != 0:
                    print(j + "<p></p>")
                    for y in a.get(i).get(j):
                        print(y)
                        print(a.get(i).get(j).get(y) + "<p></p>")
                else:
                    print(j)
                    print("OK<p></p>" )


output_inf(text)
