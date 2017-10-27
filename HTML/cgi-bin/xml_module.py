import xml.etree.cElementTree as ET
from xml.etree.cElementTree import ParseError
from xml.parsers import expat
from os import listdir, path
from collections import OrderedDict


class KeysObject:
    dict_bits = []
    in_type = ''
    out_type = ''
    norm_val = ''
    direction = ''
    name = ''

    def __init__(self):
        self.dict_bits = []

    def __str__(self):
        return "name = {}, norm_val = {}, in_type = {}, out_type = {}".format(self.name, self.norm_val, self.in_type, self.out_type)

    def __repr__(self):
        return self.__str__()


class BitsObject:
    name = ''
    index = None
    value = None
    width = None
    text_of_bit = None

    def __init__(self):
        self.list_in_bits = []

    def get_width(self):
        if not self.width:
            return self.get_value()
        split_width = self.width.split("-")
        if len(split_width) > 2:
            return self.get_value()
        try:
            return sum([2 ** i for i in range(int(split_width[0]), int(split_width[1]))])
        except ValueError:
            return self.get_value()

    def get_value(self):
        if self.index:
            return 2 ** int(self.index)
        return int(self.value)

    def bit_is_active(self, value):
        print "{:032b}\n{:032b}\n\n".format(value, self.get_value())
        return value & self.get_width() == self.get_value()

    def __str__(self):
        return str(self.name) + " " + str(self.index) + " " + str(self.text_of_bit)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name and self.index == other.value and self.text_of_bit == other.text_of_bit


class ConfigObject:
    name_key = ''
    name_of_CANDY = ''
    header = ''
    list_of_keys_to_print = []
    root_limiter = ''
    active_key_limiter = ''
    list_of_object_keys = []

    def __str__(self):
        return (str(self.name_key) + " " + str(self.header) + " " + str(self.root_limiter) + " " + str(
            self.active_key_limiter) + " " + str(self.list_of_object_keys))

    def __repr__(self):
        return self.__str__()

    def __init__(self):
        self.list_of_object_keys = []


class ConfigModule:
    list_of_active_keys = []

    def __init__(self, version):
        self.version = version.replace("\n", "")

    def check_path(self):
        true_path = ''

        if path.exists('cgi-bin/config'):
            true_path = 'cgi-bin/config/'
        elif path.exists('config'):
            true_path = 'config/'
        elif path.exists('../config'):
            true_path = '../config/'
        elif path.exists('../../config'):
            true_path = '../../config/'

        return true_path

    # check all files in config directory and return dictionary of keys and files name
    def get_keys_from_files(self):
        list_of_limiters = []

        dict_of_keys = OrderedDict()

        list_of_files = listdir(self.check_path())

        for i in list_of_files:
            if i[len(i) - 4: len(i)] == ".xml":
                i = i.replace("[", "").replace("]", "").replace("'", "")
                tree = None
                try:
                    tree = ET.ElementTree(file=self.check_path() + i)
                except ParseError as text:
                    dict_of_keys[i] = "Wrong xml file: "+str(text)+" in file "
                if tree:
                    try:
                        if str(tree.find('RELEASE').text).find(self.version) != -1:
                            list_of_limiters = tree.getroot().attrib.get("limiter")
                            dict_of_keys[i] = list_of_limiters
                    except AttributeError as text_2:
                        dict_of_keys[i] = "Wrong xml file: "+" No tag RELEASE"+" in file "
        return dict_of_keys

    # function that return keys with their types
    def get_list_objects(self, true_config=None):
        testetet = 0
        list_of_objects = {}
        # run by list of files
        for i in true_config:
            testetet += 1
            # create a empty object of file
            file_object = ConfigObject()
            # open xml config file

            tree = ET.ElementTree(file=self.check_path() + i.file_name)
            # get header from config.xml
            file_object.name_of_CANDY = i.file_name

            file_object.header = tree.find('HEADER').text
            file_object.name_key = tree.find('NAME_KEY').text
            file_object.active_key_limiter = tree.find('ACTIVE_KEYS').attrib.get("limiter")

            if not tree.find('PRINT_KEYS').text:
                file_object.list_of_keys_to_print = []
            else:
                file_object.list_of_keys_to_print = tree.find('PRINT_KEYS').text.split(" ")

            # run by xml file
            for item in tree.iterfind('.ACTIVE_KEYS/'):
                key_object = KeysObject()
                key_object.name = item.tag

                # key_object.name = key_object.name.replace("_","\s+")

                key_object.in_type = (item.attrib).get("in_type")
                key_object.out_type = (item.attrib).get("out_type")
                key_object.direction = (item.attrib).get("direction")
                key_object.norm_val = (item.attrib).get("norm_val")

                for bits in item:

                    bit_object = BitsObject()
                    bit_object.name = bits.tag

                    for disc in bits:

                        in_object = BitsObject()
                        in_object.name = disc.tag
                        in_object.text_of_bit = disc.text
                        in_object.index = disc.attrib.get("index")
                        in_object.value = disc.attrib.get("value")
                        in_object.width = disc.attrib.get("width")
                        if in_object not in bit_object.list_in_bits:
                            bit_object.list_in_bits += [in_object]
                        # list_sub_objects = in_object
                    # if list_sub_objects:

                    bit_object.text_of_bit = bits.text
                    bit_object.index = bits.attrib.get("index")
                    bit_object.value = bits.attrib.get("value")
                    bit_object.width = bits.attrib.get("width")
                    # magic
                    key_object.dict_bits += [bit_object]
                file_object.list_of_object_keys.append(key_object)

            i.xml_file_obj = file_object

        return true_config
