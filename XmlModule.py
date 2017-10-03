import xml.etree.ElementTree as ET


class ConfigObject:
    name_key = ''
    value = None
    text_of_bit = None
    header = ''
    list_of_keys_to_print = []
    root_limiter = ''
    active_key_limiter = ''
    norm_val = ''
    dict_type_of_keys = {}
    #
    # def __init__(self, name=None, text_of_bit=None, value=None):
    #     self.name = name
    #     self.value = value
    #     self.text_of_bit = text_of_bit

    def __str__(self):
        return (str(self.header) + " " + str(self.name_key) + " " + str(self.root_limiter))
    def __repr__(self):
        return self.__str__()


class ConfigModule(object):
    key_tag = ['root','HEDER','NAME_KEY','ACTIVE_KEYS']
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
       list_of_objects = []
#run by list of files
       for i in true_config:
#create a empty object of file
         file_object = ConfigObject()
#open xml config file
         tree = ET.ElementTree(file="config\\" + i)
         file_object.header=tree.find('HEDER').text
         file_object.name_key = tree.find('NAME_KEY').text
         file_object.root_limiter = tree.getroot().attrib.get("limiter")
         # print(file_object.header)
         # print(file_object.name_key)
         # print(file_object.root_limiter)
         #
         # # for x in tree.iterfind('root'):
         # #     file_object.header = x.text
         # # print(file_object.header)
         for item in tree.iterfind('.ACTIVE_KEYS/'):
            file_object.dict_type_of_keys[item.tag] = (item.attrib).get("type")
            for bits in item:
                bit_object = ConfigObject()
                bit_object.name = bits.tag
                bit_object.text_of_bit = bits.text
                bit_object.value = bits.attrib.get("value")

                if item.tag in self.dict_bits:
                    self.dict_bits[item.tag] += [bit_object]
                else:
                    self.dict_bits[item.tag] = [bit_object]
         list_of_objects.append(file_object)

       return list_of_objects

#object1 = ConfigModule()
#print(object1.get_list_objects(["rxbsp.xml","rxcap.xml"]))
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
