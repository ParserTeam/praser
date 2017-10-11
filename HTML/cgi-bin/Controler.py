from PrintReader import PrintReader
from XmlModule import ConfigModule
from interface import select_version, get_input_inf, output_inf


class Controller:
    print_reader = None
    xml_files = None
    xml_reader = None

    def __init__(self):
        self.xml_reader = ConfigModule()
        self.xml_files = self.xml_reader.get_keys_from_files()

    def check_text(self, print_text):
        """
        Main function to check text
        :param print_text: text with printouts
        :return: dict:
                    key: xml_file name
                    value: list of dict printout for this file:
                            dict:
                                key: key name (MO, NSEI, ...)
                                value: dict with decode info:
                                    key: short decode
                                    value: long decode
        example =
        """
        self.print_reader = PrintReader(print_text, self.xml_files)
        if len(self.print_reader.subjects) == 0:
            return "<b>No file found for text</b><p>Files available: " + ", ".join(self.xml_files.keys()) + "</p>"
        self._check_file_version(self.print_reader.subjects)
        list_check_values = self.print_reader.get_check_values()
        # return list_check_values
        return self.create_data_for_out(list_check_values)

    def create_data_for_out(self, list_check_values):
        result = dict()

        # return list_check_values
        for check_value in list_check_values:
            xml_object = check_value.xml_obj
            for dictionary_of_subject in check_value.parse_objects:
                errors = self.checker_bits(dictionary_of_subject, xml_object)
                if errors:
                    # if check_value.add_to_print:
                    #     errors.update(check_value.add_to_print)
                    if not result.get(check_value.xml_file_name):
                        result[check_value.xml_file_name] = [errors]
                    else:
                        result[check_value.xml_file_name] += [errors]
                        # result[check_value.xml_file_name] = "Everything is OK. Go drink coffee :)"
        return result

    # function for check bits and return list of print cases
    def checker_bits(self, printout_bits=None, config_bits=None):
        print_out_for_view = {}

        keys = config_bits

        for i_obj in keys.list_of_object_keys:
            bits = i_obj
            bit = bits.dict_bits

            if bits.type.isdigit():
                if printout_bits.get(bits.name) == '':
                    value = 0
                else:
                    value = int(str(printout_bits.get(bits.name)), int(bits.type))
                value_in_bits = (format(value, "0>42b"))
                value_in_bits_revers = value_in_bits[::-1]
                printout_bits[bits.name] = {}
                for i in range(0, len(value_in_bits_revers)):

                    if value_in_bits_revers[i] != str(bits.norm_val):
                        try:
                            printout_bits[bits.name][bit[i].name] = bit[i].text_of_bit
                        except IndexError:
                            pass
            if bits.type.isalpha():
                work_dict = {}
                string_value = printout_bits.get(bits.name)
                # work_dict =  printout_bits[bits.name]
                if string_value != str(bits.norm_val):
                    try:
                        work_dict = printout_bits
                    except IndexError:
                        work_dict = {}
                else:
                    work_dict = {}
                printout_bits = work_dict
                # printout_bits[bits.name][cheker.name].popitem(cheker.text_of_bit)

        return printout_bits

    def _check_file_version(self,list_ojects):
        for obj in range(len(list_ojects)):
            if len(list_ojects[obj].file_names) > 1:
                list_ojects[obj].file_names = select_version(list_ojects[obj].file_names, list_ojects[obj].text)
        self.xml_reader.get_list_objects(list_ojects)


if __name__ == "__main__":
    controller = Controller()
    input_text = get_input_inf()
    text = controller.check_text(input_text)
    output_inf(text)
