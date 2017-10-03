import xml.etree.ElementTree as ET


class KeysObject:
    dict_bits = {}
    type = ''
    norm_val = ''
    start = ''
    end = ''

    def __str__(self):
        return (str(self.type) + " " + str(self.norm_val) + " " + str(self.start) + " " + str(self.end) + " " + str(
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
    header = ''
    list_of_keys_to_print = []
    root_limiter = ''
    active_key_limiter = ''
    list_of_object_keys = []

    #
    # def __init__(self, name=None, text_of_bit=None, value=None):
    #     self.name = name
    #     self.value = value
    #     self.text_of_bit = text_of_bit

    def __str__(self):
        return (str(self.name_key) + " " + str(self.header) + " " + str(self.root_limiter) + " " + str(
            self.active_key_limiter) + " " + str(self.list_of_object_keys))

    def __repr__(self):
        return self.__str__()


class ConfigModule(object):
    # key_tag = ['root','HEDER','NAME_KEY','ACTIVE_KEYS']
    list_of_keys = []
    list_of_active_keys = []
    dict_bits = {}

    # check all files in config directory and return dictionary of keys and files name
    def get_keys_from_files(self):
        from os import listdir

        dict_of_keys = {}
        list_of_files = listdir("config")

        for i in list_of_files:
            try:
                i = i.replace("[", "").replace("]", "").replace("'", "")
                tree = ET.ElementTree(file="config\\" + i)

                list_of_keys = str(tree.findtext('KEYS')).split(' ')
                dict_of_keys[i] = list_of_keys
            except FileNotFoundError:
                return {}
        return dict_of_keys

    # function that return keys with their types
    def get_list_objects(self, true_config):
        list_of_objects = {}
        # run by list of files
        for i in true_config:
            # create a empty object of file
            file_object = ConfigObject()
            # open xml config file
            tree = ET.ElementTree(file="config\\" + i)
            file_object.header = tree.find('HEDER').text
            file_object.name_key = tree.find('NAME_KEY').text
            file_object.root_limiter = tree.getroot().attrib.get("limiter")
            file_object.active_key_limiter = tree.find('ACTIVE_KEYS').attrib.get("limiter")
            file_object.list_of_keys_to_print = tree.find('PRINT_KEYS').text

            for item in tree.iterfind('.ACTIVE_KEYS/'):
                key_object = KeysObject()
                key_object.type = (item.attrib).get("type")
                key_object.start = (item.attrib).get("start")
                key_object.end = (item.attrib).get("end")
                key_object.norm_val = (item.attrib).get("norm_val")
                for bits in item:
                    bit_object = BitsObject()
                    bit_object.name = bits.tag
                    bit_object.text_of_bit = bits.text
                    bit_object.value = bits.attrib.get("bit")

                    if item.tag in key_object.dict_bits:
                        key_object.dict_bits[item.tag] += [bit_object]
                    else:
                        key_object.dict_bits[item.tag] = [bit_object]
                file_object.list_of_object_keys.append(key_object)

            list_of_objects[i] = file_object

        return list_of_objects


#object1 = ConfigModule()
#print(object1.get_list_objects(["rxcap.xml"]))
# print(object1.get_dict_with_properties('rxbsp.xml'))
# print(object1.get_name_key_mo('rxcap.xml'))
# print(object1.get_bits_value())
# test_dict = object1.get_bits_value()
# for key, value in test_dict.items():
#   print(key)
#   for el in value:
#      print(el)
# for i in test_dict.values():
#    print(i)
