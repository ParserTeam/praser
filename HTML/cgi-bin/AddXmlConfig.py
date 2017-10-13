import cgi
import xml.etree.ElementTree as xml
from xml.dom import minidom
from os import listdir

form = cgi.FieldStorage()

limiter = ''
header = ''
name_of_file = ''
keys = ''
name_key = ''
keys_to_print = ''
in_type = []
out_type = []
direction = []
norm_value = []
list_of_bits = []

for i in form.list:
    if i.name == "limiter":
        limiter = i.value
    elif i.name == "nameFile":
        name_of_file = i.value
    elif i.name == "keys":
        keys = i.value
    elif i.name == "name_key":
        name_key = i.value
    elif i.name == "KeysToPrint":
        keys_to_print = i.value
    elif i.name == "Header":
        header = i.value
    elif i.name == "in_type":
        in_type.append(i.value)
    elif i.name == "out_type":
        out_type.append(i.value)
    elif i.name == "direct":
        direction.append(i.value)
    elif i.name == "norm_val":
        norm_value.append(i.value)



list_keys = keys.split(" ")

number = 0

for length in range(0, len(list_keys)):

    for j in form.list:
        if j.name == list_keys[length]:
            list_of_bits.append(j)
    list_of_bits.append(list_keys[length])

doc = minidom.Document()

root = doc.createElement('root')
root.setAttribute('limiter', limiter)
doc.appendChild(root)

header_tag = doc.createElement('HEADER')
header_text = doc.createTextNode(header)
header_tag.appendChild(header_text)
root.appendChild(header_tag)

keys_tag = doc.createElement('KEYS')
keys_text = doc.createTextNode(keys)
keys_tag.appendChild(keys_text)
root.appendChild(keys_tag)

name_key_tag = doc.createElement('NAME_KEY')
name_key_text = doc.createTextNode(name_key)
name_key_tag.appendChild(name_key_text)
root.appendChild(name_key_tag)

active_keys_tag = doc.createElement('ACTIVE_KEYS')
root.appendChild(active_keys_tag)

for i in range(0, len(list_keys)):
    key_tag = doc.createElement(list_keys[i])
    try:
        key_tag.setAttribute('in_type', in_type[i])
    except IndexError:
        pass
    try:
        key_tag.setAttribute('out_type', out_type[i])
    except IndexError:
        pass
    try:
        key_tag.setAttribute('direction', direction[i])
    except IndexError:
        pass
    try:
        key_tag.setAttribute('norm_val', norm_value[i])
    except IndexError:
        pass

    for j in list_of_bits:
        if (type(j) != str) and (j.name == list_keys[i]):

            bit_name = j.value[:j.value.find(" ")]
            j.value = j.value[j.value.find(" ") + 1:]

            bit_value = j.value[:j.value.find(" ")]
            j.value = j.value[j.value.find(" ") + 1:]

            bit_tag = doc.createElement(bit_name)
            bit_tag.setAttribute("bit", bit_value)
            bit_text = doc.createTextNode(j.value)
            bit_tag.appendChild(bit_text)
            key_tag.appendChild(bit_tag)
        else:
            continue
    # continue
    # key_text = doc.createTextNode("h1 12 asdkasljdklajdklasjk")

    # key_tag.appendChild(key_text)
    active_keys_tag.appendChild(key_tag)

keys_to_print_tag = doc.createElement('PRINT_KEYS')
keys_to_print_text = doc.createTextNode(keys_to_print)
keys_to_print_tag.appendChild(keys_to_print_text)
root.appendChild(keys_to_print_tag)

list_of_files = listdir('config/')

xml_str = doc.toprettyxml(indent="  ")

for file in list_of_files:
    if name_of_file + ".xml" == file:
        if name_of_file[len(name_of_file)-1:len(name_of_file)].isdigit:
            pass # file_name_for_creating =
        break
    else:
        file_name_for_creating = "config\\" + name_of_file + ".xml"

with open(file_name_for_creating, "w") as f:
    f.write(xml_str)



print """
<html>
Sucsses!!!
{}
</html>
""".format(list_of_files)
