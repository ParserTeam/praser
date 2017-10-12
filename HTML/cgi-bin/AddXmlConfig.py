import cgi

form = cgi.FieldStorage()
list1212 = form.list

config_file = ''




print """
<html>
Sucsses!!!
{}
</html>
""".format(list1212)










