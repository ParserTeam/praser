class ConfigModule(object):
    from re import search
    list_of_keys = []
    ist_of_active_keys = []
    header = ''
    list_of_keys_to_print = []

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
                dict_of_keys[i] = list_of_keys

            except FileNotFoundError:
                dict_of_keys = {}
                return dict_of_keys
        return dict_of_keys
#function that return keys with their types
    def get_dict_with_properties(self, true_config):
        import xml.etree.cElementTree as ET
        dict_type_of_keys = {}
        tree = ET.ElementTree(file="config\\" + true_config)
        for item in tree.iterfind('.ACTIVE_KEYS/'):
            dict_type_of_keys[item.tag] = (item.attrib).get("type")
            print(item.attrib)
            print(item.tag)
        return dict_type_of_keys


