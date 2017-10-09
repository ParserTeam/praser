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
    if len(a) != 0 :
        print('''
            <link rel="stylesheet" type="text/css" href="style.css">
            <link rel='stylesheet prefetch' href='http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css'>
            <link rel='stylesheet prefetch' href='http://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.10.0/bootstrap-table.min.css'>
            <link rel='stylesheet prefetch' href='http://rawgit.com/vitalets/x-editable/master/dist/bootstrap3-editable/css/bootstrap-editable.css'>
            <div class="container">
			 <table class="table table-bordered">
        ''')
        for i in a:
            print('''
                                <tr>
                                        <th colspan="4" ></th>
                                </tr>
                            ''')
            print('''
                <tr>
					<th colspan="4" >''' + i[:i.find(".")].upper() + '''</th>
				</tr>
            ''')
            for j in a.get(i):
                b = j
                print('''
                    <tr>
                            <th colspan="4" ></th>
                    </tr>
                ''')
                for z in b:
                    if type(b.get(z)) != dict:
                        print('''
                            <tr class="bg-primary">
                              <th>''' + z + ''' -''' + '''</th>
                              <th colspan="3" >''' + b.get(z) + ''' ;''' + '''</th>
                            </tr>
                        ''')
                    else:
                        if len(b.get(z)) != 0:
                            print('''
                                <tr class="bg-success ">
                                  <th>''' + z + ''' :''' +'''</th>
                                  <th colspan="3" >ERRORS:</th>
                                </tr>
                            ''')
                            for y in b.get(z):
                                print('''
                                    <tr class="bg-success ">
                                      <th>''' + y + ''' -''' + '''</th>
                                      <th colspan="3" >''' + b.get(z).get(y) + ''' ;''' + '''</th>
                                    </tr>
                                ''')
                        else:
                            print('''
                                <tr class="bg-success ">
                                  <th>''' + z + ''' -''' + '''</th>
                                  <th colspan="3" >OK;</th>
                                </tr>
                            ''')
        print('''
                    </table>
		    </div>
                ''')

output_inf(text)

