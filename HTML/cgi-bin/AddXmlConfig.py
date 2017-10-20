import cgi
from xml.dom import minidom
import Tkinter
from tkSimpleDialog import askstring
from os import listdir
import re

from re import search


class CreateXml:
    form = cgi.FieldStorage()

    limiter = form.getvalue("limiter") or ""
    header = form.getvalue("Header") or ""
    name_of_file = form.getvalue("nameFile") or ""
    keys = form.getvalue("keys") or ""
    name_key = form.getvalue("name_key") or ""
    keys_to_print = form.getvalue("KeysToPrint") or ""
    in_type = []
    out_type = []
    direction = []
    norm_value = []
    list_keys = keys.split(" ")

    doc = minidom.Document()
    root = doc.createElement('root')
    doc.appendChild(root)

    for i in form.list:
        if i.name == "in_type":
            in_type.append(i.value)
        elif i.name == "out_type":
            out_type.append(i.value)
        elif i.name == "direct":
            direction.append(i.value)
        elif i.name == "norm_val":
            norm_value.append(i.value)

    list_of_bits = []
    for length in range(0, len(list_keys)):

        for j in form.list:
            if j.name == list_keys[length]:
                list_of_bits.append(j)
        list_of_bits.append(list_keys[length])

    def create_root(self):
        self.root.setAttribute('limiter', self.limiter)

    def create_header(self):
        header_tag = self.doc.createElement('HEADER')
        header_text = self.doc.createTextNode(self.header)
        header_tag.appendChild(header_text)
        return header_tag

    # def create_key
    #     keys_tag = doc.createElement('KEYS')
    #     keys_text = doc.createTextNode(keys)
    #     keys_tag.appendChild(keys_text)
    #     root.appendChild(keys_tag)
    def create_name_key(self):
        name_key_tag = self.doc.createElement('NAME_KEY')
        name_key_text = self.doc.createTextNode(self.name_key)
        name_key_tag.appendChild(name_key_text)
        return name_key_tag

    def create_active_keys(self):
        active_keys_tag = self.doc.createElement('ACTIVE_KEYS')
        # root.appendChild(active_keys_tag)

        for i in range(0, len(self.list_keys)):
            key_tag = self.doc.createElement(self.list_keys[i])
            try:
                key_tag.setAttribute('in_type', self.in_type[i])
            except IndexError:
                pass
            try:
                key_tag.setAttribute('out_type', self.out_type[i])
            except IndexError:
                pass
            try:
                key_tag.setAttribute('direction', self.direction[i])
            except IndexError:
                pass
            try:
                key_tag.setAttribute('norm_val', self.norm_value[i])
            except IndexError:
                pass

            for j in self.list_of_bits:
                if (type(j) != str) and (j.name == self.list_keys[i]):

                    bit_name = j.value[:j.value.find(" ")]
                    j.value = j.value[j.value.find(" ") + 1:]

                    bit_value = j.value[:j.value.find(" ")]
                    j.value = j.value[j.value.find(" ") + 1:]

                    bit_tag = self.doc.createElement(bit_name)
                    bit_tag.setAttribute("bit", bit_value)
                    bit_text = self.doc.createTextNode(j.value)
                    bit_tag.appendChild(bit_text)
                    key_tag.appendChild(bit_tag)
                else:
                    continue

            active_keys_tag.appendChild(key_tag)
        return active_keys_tag

    def create_keys_to_print(self):
        keys_to_print_tag = self.doc.createElement('PRINT_KEYS')
        keys_to_print_text = self.doc.createTextNode(self.keys_to_print)
        keys_to_print_tag.appendChild(keys_to_print_text)
        return keys_to_print_tag


class WriteXml(CreateXml):
    file_name_for_creating = ''

    # XmlText.doc.appendChild(XmlText.create_root())
    # root = XmlText.create_root()


    def __init__(self):

        # self.root = self.create_root()
        # self.doc.appendChild(self.root)
        self.root.appendChild(self.create_header())
        self.root.appendChild(self.create_name_key())
        self.root.appendChild(self.create_active_keys())
        self.root.appendChild(self.create_keys_to_print())

        self.list_of_files = listdir('config/')

        self.xml_str = self.doc.toprettyxml(indent="  ")

        self.list_of_same_files = [xml_file for xml_file in self.list_of_files if self.name_of_file in xml_file]

        # self._create_name_of_suggest()
        self.file_name_for_creating = self._create_name_of_suggest()
        self._show_user_message_box()
        self.file_name_for_creating = "config\\" + self.file_name_for_creating

        with open(self.file_name_for_creating, "w") as f:
            f.write(self.xml_str)

        self._show_created_xml()

    def _check_in_array(self, name, file):
        element = re.sub(name + r"\D*(\d*).xml", lambda x: name + "_ver" + str(int(x.group(1) or 0) + 1) + ".xml", file)
        return element

    def _create_name_of_suggest(self):
        for file in self.list_of_same_files:
            if not self._check_in_array(self.name_of_file, file) in self.list_of_same_files:
                return self._check_in_array(self.name_of_file, file)

    def _dry(self):
        self.file_name_for_creating = askstring('Test TEs', 'How deep is your love?',
                                                initialvalue=self._create_name_of_suggest())+".xml"

    def _show_user_message_box(self):
        flag = True
        root = Tkinter.Tk()
        root.withdraw()
        # root.minsize(width=100, height=200)

        self._dry()

        while flag:
            if not self.file_name_for_creating in self.list_of_same_files:
                break
            else:
                self._dry()

    def _show_created_xml(self):
        file_test = open(self.file_name_for_creating, "r")

        text = file_test.read()

        file_test.close()
        print """

            Sucsses!!!
            {}
             """.format(text)

        # file_name_for_creating = "config\\" + file_name_for_creating
        # with open(file_name_for_creating, "w") as f:
        #     f.write(xml_str)


objectXml = WriteXml()
