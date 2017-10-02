
class ConfigModule(object):
    import os
    import xml.etree.cElementTree as ET
    from re import search
    # connect to config directory
    list_of_files = os.listdir("config")

    list_of_keys = []
    list_of_active_keys = []
    header = ''
    list_of_keys_to_print = []
    #open print_out
    file = open("rxbsp.txt", "r")
    print_out = file.read()
    print(print_out)
    file.close()

    #find true config file
    for i in list_of_files:
        try:
            i = i.replace("[", "").replace("]", "").replace("'", "")
            tree = ET.ElementTree(file="config\\" + i)
            list_of_keys = str(tree.findtext('ALL_KEYS')).split(' ')

            regular = r''
            for j in list_of_keys:
                regular = regular + str(j) + ".*"
            regular = regular + "\\n"
            check = search(regular, print_out)
            try:
                if type(check.group()) != "NoneType":
                       true_config = i
            except AttributeError:
                print("File with config not found")

        except FileNotFoundError:
            print("File with config not found")

    print(true_config)

    # get list of keys from config file
    def work_with_xml(self, true_config):
        pass
