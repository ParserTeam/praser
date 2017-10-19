import cgi, cgitb
form = cgi.FieldStorage()
f= form.getvalue('txt')

file = open('.\config\\versions.txt','a')
file.write('\n'+f)
file.close()
file = open('.\config\\versions.txt','r')

for line in file:
    print line

file.close()