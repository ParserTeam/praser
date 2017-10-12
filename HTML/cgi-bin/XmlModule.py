import xml.etree.cElementTree as ET
from xml.etree.cElementTree import ParseError
from os import listdir, path


class KeysObject:
    dict_bits = []
    type = ''
    norm_val = ''
    start = ''
    end = ''
    name = ''

    def __init__(self):
        self.dict_bits = []

    def __str__(self):
        return (
            str(self.type) + " " + str(self.norm_val) + " " + str(self.start) + " " + str(self.end) + " " + " " + str(
                self.name) + " " + str(
                self.dict_bits))

    def __repr__(self):
        return self.__str__()


class BitsObject:
    name = ''
    value = None
    text_of_bit = None

    def __str__(self):
        return (str(self.name) + " " + str(self.value) + " " + str(self.text_of_bit))

    def __repr__(self):
        return self.__str__()


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


class ConfigModule():
    list_of_active_keys = []

    # check all files in config directory and return dictionary of keys and files name
    def get_keys_from_files(self):
        list_of_limiters = []

        dict_of_keys = {}
        if path.exists('cgi-bin/config'):
            list_of_files = listdir('cgi-bin/config')
        elif path.exists('config'):
            list_of_files = listdir('config')
        elif path.exists('../config'):
            list_of_files = listdir('../config')

        # scriptpath = path.dirname("config")

        for i in list_of_files:
            if i[len(i) - 4: len(i)] == ".xml":
                i = i.replace("[", "").replace("]", "").replace("'", "")
                tree = None
                try:
                    if path.exists('cgi-bin/config/'):
                        tree = ET.ElementTree(file='cgi-bin/config/' + i)
                    elif path.exists('config/'):
                        tree = ET.ElementTree(file='config/' + i)
                    elif path.exists('../config/'):
                        tree = ET.ElementTree(file='../config/' + i)
                except ParseError:
                    pass
                # list_of_limiters = str(tree.findtext('KEYS')).split(' ')
                if tree:
                    list_of_limiters = tree.getroot().attrib.get("limiter")
                    dict_of_keys[i] = list_of_limiters
        return dict_of_keys


# function that return keys with their types
    def get_list_objects(self, true_config=None):
        list_of_objects = {}
        # run by list of files
        for i in true_config:
            # create a empty object of file
            file_object = ConfigObject()
            # open xml config file
            try:
                if path.exists('cgi-bin/config/'):
                    tree = ET.ElementTree(file='cgi-bin/config/' + i.file_names[0])
                elif path.exists('config/'):
                    tree = ET.ElementTree(file='config/' + i.file_names[0])
                elif path.exists('../config/'):
                    tree = ET.ElementTree(file='../config/' + i.file_names[0])
            except ParseError:
                pass
            # get header from config.xml
            file_object.name_of_CANDY = i.file_names[0]

            file_object.header = tree.find('HEDER').text
            # get name of key from config.xml
            file_object.name_key = tree.find('NAME_KEY').text
            # get regular expression from config.xml
            file_object.active_key_limiter = tree.find('ACTIVE_KEYS').attrib.get("limiter")
            # get keys which we will printout from config.xml
            file_object.list_of_keys_to_print = tree.find('PRINT_KEYS').text
            # run by xml file
            for item in tree.iterfind('.ACTIVE_KEYS/'):
                # create object of class KeysObject
                key_object = KeysObject()
                key_object.name = item.tag
                # get type of notation
                key_object.type = (item.attrib).get("type")
                # get start
                key_object.start = (item.attrib).get("direction")
                # get value of bits
                key_object.norm_val = (item.attrib).get("norm_val")
                # run by keys sub tags
                # print('###########')
                for bits in item:
                    # create object of bit
                    bit_object = BitsObject()
                    # get name of bit
                    bit_object.name = bits.tag
                    # get description of bit
                    bit_object.text_of_bit = bits.text
                    # get value of bit
                    bit_object.value = bits.attrib.get("bit")
                    # magic
                    key_object.dict_bits += [bit_object]
                file_object.list_of_object_keys.append(key_object)
            # add file object to list
            # list_of_objects[i.file_names[0]] = file_object
            i.xml_file_obj = file_object
        # return list of objects
        return true_config
# #
# # #

