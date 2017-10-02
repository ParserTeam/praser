class ConfigModule(object):
    from re import search

    list_of_keys = []
    list_of_active_keys = []
    header = ''
    list_of_keys_to_print = []

    def get_dit_from_files(self):
        from os import listdir
        import xml.etree.cElementTree as ET
        dict_of_keys = {}
        list_of_files = listdir("config")
        for i in list_of_files:
            try:
                i = i.replace("[", "").replace("]", "").replace("'", "")
                print(i)
                tree = ET.ElementTree(file="config\\" + i)
                list_of_keys = str(tree.findtext('KEYS')).split(' ')
                dict_of_keys[i] = list_of_keys
                return dict_of_keys
            except FileNotFoundError:
                dict_of_keys = {}
                return dict_of_keys


    def work_with_xml(self):
        import xml.etree.cElementTree as ET
        tree = ET.ElementTree(file="config\\" + self)
        print(tree)
        for item in tree.iterfind('.ACTIVE_KEYS//'):
            # print('Find: %s' % item.tag)
            # print(item.items)
            print(item.tag)
            print(item.text)
