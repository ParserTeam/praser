import sys
from tkinter import filedialog
from PrintReader import PrintReader
from XmlModule import ConfigModule
#from interface import get_input_inf,output_inf


class Controller:
    print_reader = None
    xml_files = None
    xml_reader = None

    def __init__(self):
        self.xml_reader = ConfigModule()
        self.xml_files = self.xml_reader.get_keys_from_files()

    def check_text(self, text):
        self.print_reader = PrintReader(text, self.xml_files)
        xml_objects = self.xml_reader.get_list_objects(self.print_reader.get_config_files_in_text())
        if not xml_objects:
            return "<b>No file found for text</b>"
        self.print_reader.make_subjects(xml_objects)
        list_check_values = self.print_reader.get_check_values()
        return list_check_values
        return self.create_data_for_out(list_check_values)

    def create_data_for_out(self, list_check_values):
        result = dict()

        #return list_check_values
        for check_value in list_check_values:
            xml_object = check_value.xml_obj
            for dictionary_of_subject in check_value.parse_objects:
                errors = self.checker_bits(dictionary_of_subject, xml_object)
                if errors:
                    result[check_value.xml_file_name] = errors
                else:
                    result[check_value.xml_file_name] = "Everything is OK. Go drink coffee :)"
        return result


# function for check bits and return list of print cases
    def checker_bits(self, printout_bits=None, config_bits=None):
        print_out_for_view = {}

        keys = config_bits


        for i_obj in keys.list_of_object_keys:
            bits = i_obj
            bit = bits.dict_bits
# if type is digit we have one way
            if bits.type.isdigit():
                value = int(str(printout_bits.get(bits.name)), int(bits.type))
                value_in_bits = (format(value, "0>42b"))
                value_in_bits_revers = value_in_bits[::-1]
                printout_bits[bits.name] = {}
                for i in range(0, len(value_in_bits_revers)):

                    if value_in_bits_revers[i] != str(bits.norm_val):
                        try:
                            printout_bits[bits.name][bit[i].name] = bit[i].text_of_bit
                            #printout_bits{bits.name:dict()[bit[i].name]}

                            # print_out_for_view.append(bit[i].name)
                            # print_out_for_view.append(bit[i].text_of_bit)
                            #print_out_for_view.append(bit[i].name)
                        except IndexError:
                            pass
                    # else:
                    #     print_out_for_view.append(None)
#if type is string we have another way
            if bits.type.isalpha():
                string_value = printout_bits.get(bits.name)
                printout_bits[bits.name] = {}
                if string_value != str(bits.norm_val):
                    try:
                        printout_bits[bits.name][bit.name] = bit.text_of_bit
                        # print_out_for_view.append(bit)
                        # print_out_for_view.append(bit.name)
                    except IndexError:
                        pass
                # else:
                #     print_out_for_view.append(None)

        return printout_bits









# controller = Controller()
# test = ConfigModule()
# # objectTest = C
# # controller.checker_bits("10001")
# # on button click
# # output_inf(controller.checker_bits({"BVCI": "123", "CELL": "113020C", "OPCONDMAP": "04", "IPDEV": "RTIPGPH-2"},
# #                               test.get_list_objects(['rxbsp.xml'])))
# # # controller.check_text()
#
# print(controller.checker_bits({"BVCI": "123", "CELL": "113020C", "OPCONDMAP": "04", "IPDEV": "RTIPGPH-2"},
#                               test.get_list_objects(['rxbsp.xml'])))

# if controller.no_subjects():
#   print("Can't find eny subject to read")
#    exit(0)
# end on button click
