from re import *
import xml.etree.cElementTree as ET

tree = ET.ElementTree(file = config.xml)
print tree.getroot()
print type(tree.getroot())

file = open("New Text Document.txt","r")
text = file.read()

file_rxbsp = open("rxbsp.txt","r")
text_rxbsp = file_rxbsp.read()
