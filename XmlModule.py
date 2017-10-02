class KeysObject:
    name = None
    value = None
    text_of_bit = None

    def __init__(self, name=None, text_of_bit=None, value=None):
        self.name = name
        self.value = value
        self.text_of_bit = text_of_bit
    def __str__(self):
        return (str(self.name)+" "+str(self.value)+" "+str(self.text_of_bit))


class ConfigModule(object):
    from re import search

    list_of_keys = []
    ist_of_active_keys = []
    header = ''
    list_of_keys_to_print = []

    dict_bits = {}

    # check all files in config directory and return dictionary of keys
    def get_dict_from_files(self):
        from os import listdir
        import xml.etree.cElementTree as ET

        dict_of_keys = {}
        list_of_files = listdir("config")

        for i in list_of_files:
            try:
                i = i.replace("[", "").replace("]", "").replace("'", "")
                tree = ET.ElementTree(file="config\\" + i)

                list_of_keys = str(tree.findtext('KEYS')).split(' ')
                name_key_mo = tree.findtext('NAME_KEY')

                dict_of_keys[i] = (list_of_keys, name_key_mo)

            except FileNotFoundError:
                return {}
        return dict_of_keys

    # function that return keys with their types
    def get_dict_with_properties(self, true_config):
        import xml.etree.cElementTree as ET
        dict_type_of_keys = {}

        tree = ET.ElementTree(file="config\\" + true_config)

        for item in tree.iterfind('.ACTIVE_KEYS/'):
            dict_type_of_keys[item.tag] = (item.attrib).get("type")
            for bits in item:
                #print(bits.tag)
                bit_object = KeysObject()
                bit_object.name = bits.tag
                bit_object.text_of_bit = bits.text
                bit_object.value = bits.attrib.get("value")

                if item.tag in self.dict_bits:
                    self.dict_bits[item.tag] += [bit_object]
                else:
                    self.dict_bits[item.tag] = [bit_object]

        return dict_type_of_keys

    def get_bits_value(self):
        return self.dict_bits

#object1 = ConfigModule()
#print(object1.get_dict_from_files())
#print(object1.get_dict_with_properties('rxbsp.xml'))
#print(object1.get_name_key_mo('rxcap.xml'))
#print(object1.get_bits_value())
#test_dict = object1.get_bits_value()
#for key, value in test_dict.items():
#   print(key)
#   for el in value:
#      print(el)
#for i in test_dict.values():
#    print(i)