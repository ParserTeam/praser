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
    _value = None
    _width = None
    text_of_bit = None

    def __init__(self):
        self.list_in_bits = []

    def set_parameters(self, value=None, index=None, width=None):
        if index:
            self._value = 2 ** int(index)
        elif value:
            self._set_value_by_value(value, width)
        else:
            assert "Can't set value!"
        self._set_width(width)

    def _width_to_int_arr(self, width):
        split_width = width.split("-")
        return [int(val) for val in split_width]

    def _set_value_by_value(self, value, width):
        if not width:
            self._value = int(value)
        else:
            main_bit = self._width_to_int_arr(width)[0]
            self._value = (int(value) << (main_bit + 1)) + (2 ** main_bit)

    def get_value(self):
        if self._value is None:
            raise ValueError("Value not set")
        else:
            return self._value

    def _set_width(self, width):
        if not width:
            self._width = self.get_value()
        else:
            try:
                self._width = sum([2 ** i for i in range(*self._width_to_int_arr(width))])
            except ValueError:
                self._width = self.get_value()

    def get_width(self):
        return self._width

    def bit_is_active(self, value):
        # print "{:032b}\n{:032b}\n\n".format(value, self.get_value())
        if self._width == 0:
            return value == self.get_value()
        return value & self.get_width() == self.get_value()

    def __str__(self):
        return "name = {}, value = {}, width = {}, text_of_bit = {}".format(self.name, self._value, self._width, self.text_of_bit)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name and self.get_value() == other.get_value() and self.get_width() == self.get_width()


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
                key_object.name = item.tag if item.attrib.get("name") == None else item.attrib.get("name")
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
                        in_object.set_parameters(index=bits.attrib.get("index"),
                                                 value=bits.attrib.get("value"),
                                                 width=bits.attrib.get("width")
                                                 )
                        if in_object not in bit_object.list_in_bits:
                            bit_object.list_in_bits += [in_object]
                        # list_sub_objects = in_object
                    # if list_sub_objects:

                    bit_object.text_of_bit = bits.text
                    bit_object.set_parameters(index=bits.attrib.get("index"),
                                              value=bits.attrib.get("value"),
                                              width=bits.attrib.get("width")
                                              )
                    # magic
                    key_object.dict_bits += [bit_object]
                file_object.list_of_object_keys.append(key_object)

            i.xml_file_obj = file_object

        return true_config
