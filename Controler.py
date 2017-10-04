from tkinter import filedialog
from PrintReader import PrintReader
from XmlModule import ConfigModule


class Controller:
    print_reader = None
    xml_files = None
    xml_reader = None
    view = None

    def __init__(self):
        self.view = "view"
        self.xml_reader = ConfigModule()
        self.xml_files = self.xml_reader.get_keys_from_files()

    def check_text(self):
        # from View
        file_name = filedialog.askopenfile("r")
        text = file_name.read()

        self.xml_reader = ConfigModule()
        self.print_reader = PrintReader(text, self.xml_files)
        xml_objects = self.xml_reader.get_list_objects(self.print_reader.get_config_files_in_text())
        self.print_reader.make_subjects(xml_objects)
        # for subject in self.print_reader.subjects:
        #     print(str(subject))
        # print(list)
        # for key, val in list.items():
        #     print(key + "$", val)
        # for subject in self.print_reader.subjects:
        #     self.subject_check(subject)

    # def no_subjects(self):
    #     return len(self.print_reader.subjects) == 0
    #
    # def subject_check(self, subject):
    #     table = None
    #
    #     # get active keys for subject.name
    #     # xml_active_keys = self.xml_reader.get_dict_with_properties(subject.file_name)
    #     xml_active_keys = {'OMLF1': {'type': '16', 'size_h': '2'}, 'OMLF2': '16', 'RSLF1': {'type': '16', 'size_h': '3'}, 'RSLF2': '16'}
    #     print(xml_active_keys)
    #     table = subject.get_subject_in_table()
    #     print(subject.file_name + ": " + subject.name)
    #     for row in table.table:
    #         print(table.get_values_from_row(row, xml_active_keys))
    #
    # # def checker_bits(self,printout_bits=None,config_bits=None):
    # #     x=int(str(printout_bits), 2)
    # #     print(x)

    def checker_bits(self,printout_bits=None, type_file = None,config_bits=None, norm_val = None):
            keys =  config_bits.get("rxbsp.xml")
            bits     = keys.list_of_object_keys[0]
            bit = bits.dict_bits.get('OPCONDMAP')
            if type_file.isdigit:
                x=int(str(printout_bits), int(type_file))
                text = (format(x,"0>42b"))
               # text = text[0:].reverse()
                text_revers = text[::-1]
                print(text_revers)
                for i in range(len(text_revers)):
                   if text_revers[i]!=str(norm_val):
                       print(bit[i-1])



            else:
                print("String")


controller = Controller()
# controller.checker_bits("10001")
# on button click
#controller.check_text()
test = ConfigModule()
controller.checker_bits("04", "16",test.get_list_objects(['rxbsp.xml']),0)
# if controller.no_subjects():
#   print("Can't find eny subject to read")
#    exit(0)
# end on button click

