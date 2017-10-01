from tkinter import filedialog
from PrintReader import PrintReader

# from View
file_name = filedialog.askopenfile("r")
text = file_name.read()

xml_keys = {"rxbsp": ["MO", "OPCOND", "OPCONDMAP", "OMLSTAT", "RSLSTAT"]}

print_reader = PrintReader(text, xml_keys)
for subject in print_reader.subjects:
    print(subject)
