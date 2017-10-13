import cgi
import xml.etree.ElementTree as xml
from xml.dom import minidom

form = cgi.FieldStorage()
list1212 = form.list

config_file = ''

for i in form.list:
    if i.name =="limiter":
        limiter = i.value
    if i.name == "nameFile":
        name_of_file = i.value

doc = minidom.Document()

root = doc.createElement('root')
doc.appendChild(root)

leaf = doc.createElement('leaf')
text = doc.createTextNode('Text element with attributes')
leaf.appendChild(text)
leaf.setAttribute('color', 'white')
root.appendChild(leaf)

leaf_cdata = doc.createElement('leaf_cdata')
cdata = doc.createCDATASection('<em>CData</em> can contain <strong>HTML tags</strong> without encoding')
leaf_cdata.appendChild(cdata)
root.appendChild(leaf_cdata)

branch = doc.createElement('branch')
branch.appendChild(leaf.cloneNode(True))
root.appendChild(branch)

mixed = doc.createElement('mixed')
mixed_leaf = leaf.cloneNode(True)
mixed_leaf.setAttribute('color', 'black')
mixed_leaf.setAttribute('state', 'modified')
mixed.appendChild(mixed_leaf)
mixed_text = doc.createTextNode('Do not use mixed elements if it possible.')
mixed.appendChild(mixed_text)
root.appendChild(mixed)

xml_str = doc.toprettyxml(indent="  ")
# with open("config\minidom_example.xml", "w") as f:
#     f.write(xml_str)


print """
<html>
Sucsses!!!
{}
{}
</html>
""".format(limiter,name_of_file)










