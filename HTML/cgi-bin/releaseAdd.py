import cgi, cgitb

form = cgi.FieldStorage()
fadd= form.getvalue('txt') # take value from form to add new version of release
fdel  = form.getvalue('txtdel') # take value from form to delete version of release


if fdel == None and fadd == None: #if yoser press any of button (add new version of release or delete version of release) cgi will take None
    text = "You typed any version of release."

if fadd != None:
    file = open('.\config\\versions.txt','a')
    file.write('\n'+fadd)
    file.close()
    file = open('.\config\\versions.txt','r')
    text = "New version of release wos added successfully."

if fdel != None:
    fin = open('.\config\\versions.txt', )
    for line in fin.readlines():
        fin.close()
        if fdel in line:
            fin = open('.\config\\versions.txt',)
            text = fin.read()
            lines = text.split("\n")
            fin.close()
            fout = open('.\config\\versions.txt', "w")
            lines.remove(fdel)
            fout.write("\n".join(lines))
            fout.close()
            text = "Version of release wos deleted successfully."
        else:
            text = "There no such release version like: " + fdel + "."
print '''
    <html>
    <head>
    <TITLE>PARSER</TITLE>
    <link rel="stylesheet" type="text/css" href="/style.css">
    </head>
    <body>
    <div id ="goback"><p>&nbsp</p><nav><a href="/">BACK TO PARSER</a></nav><p>&nbsp</p></div>
    <div>
    <P>&#8195;'''+text+'''</P>
    <div>
    <p STYLE="color:blue">&#8195;RELEASES: '''
file = open('.\config\\versions.txt', 'r')
for line in file:
    print line +  ';'
file.close()
'''</p>'''
print '''
    </body>
    </html>
'''
