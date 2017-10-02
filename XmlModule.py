from re import *
import os
import xml.etree.cElementTree as ET


class ConfigModule(object):

 print(os.listdir("config"))
    # connect to config file
 list_of_keys = []
 list_of_active_keys = []
 header = ''
 list_of_keys_to_print = []
 try:
     tree = ET.ElementTree(file="config\\rxbsp.xml")
 except FileNotFoundError:
        print("File not found")

 list_of_keys = str(tree.findtext('ALL_KEYS')).split(' ')
 print(list_of_keys)

    # get list of keys from config file
 def work_with_xml(self, tree):
     pass
