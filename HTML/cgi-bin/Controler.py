from print_reader import PrintReader
from XmlModule import ConfigModule
from interface import get_input_inf, output_inf
from ErrorManager import ErrorManager


class Controller:
    print_reader = None
    xml_files = None
    xml_reader = None
    list_of_xml_to_use = None

    def __init__(self, version=None):
        self.xml_reader = ConfigModule(version)
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
        example: =
        {'rxbsp.xml':
            [
                {'OPCONDMAP':
                    {'F3': 'MO is degraded or not operational due to synchronization problems.'},
                    'MO': 'RXSTF-200'
                }
            ]
        }
        """
        self.print_reader = PrintReader(print_text, self.xml_files)
        if len(self.print_reader.subjects) == 0:
            return "<b>No file found for text</b><p>Files available: " + ", ".join(self.xml_files.keys()) + "</p>"
        self.xml_reader.get_list_objects(self.print_reader.subjects)
        list_check_values = self.print_reader.get_check_values()

        # print list_check_values
        # return "You in debug mode. Please comment 56, 57 line, and uncomment 58 line in Controller.py"
        return self._create_data_for_out(list_check_values)

    def _create_data_for_out(self, list_check_values):
        result = dict()

        # return list_check_values
        for check_value in list_check_values:
            xml_object = check_value.xml_obj
            for dictionary_of_subject in check_value.parse_objects:
                errors = self.checker_bits(dictionary_of_subject, xml_object)
                if errors:
                    if not result.get(check_value.xml_header):
                        result[check_value.xml_header] = [errors]
                    else:
                        result[check_value.xml_header] += [errors]
        return result

    def _valid_printout_bits(self, number, in_type,out_type):

        try:
            if out_type == "2":
                value_bin = int(str(number), int(in_type))
                value_in_bits = (format(value_bin, "0>42b"))
                value = value_in_bits[::-1]
                return value
            elif out_type == "10":
                value = int(str(number), int(in_type))
                return value
        except ValueError:
            error_manager.add_error_message()
            return None


    # function for check bits and return list of print cases
    def checker_bits(self, printout_bits=None, config_bits=None):
        print_out_for_view = {}

        keys = config_bits

        for i_obj in keys.list_of_object_keys:
            bits = i_obj

            if bits.in_type.isdigit:
                list_of_printouts = printout_bits.get(bits.name)
                printout_bits[bits.name] = {}

                for bits_name_value in list_of_printouts or []:

                    if not bits_name_value:
                        value = 0
                    else:
                        value = self._valid_printout_bits(bits_name_value,bits.in_type,bits.out_type)

                    if bits.out_type == "2":
                        for i in range(0, len(value)):

                            if value[i] != str(bits.norm_val):
                                # try:
                                for value_bit in bits.dict_bits:
                                    if value_bit.value == str(i):
                                        printout_bits[bits.name][value_bit.name] = value_bit.text_of_bit
                    if bits.out_type == "10":
                        for value_bit in bits.dict_bits:
                            if value_bit.value == str(value):
                                printout_bits[bits.name][value_bit.name] = value_bit.text_of_bit

        if self._is_all_values_is_empty(printout_bits):
            return {}
        else:
            return printout_bits
    def _is_all_values_is_empty(self, printout_bits):
        for key,val in printout_bits.items():
            if not isinstance(val, str):
                if val:
                    return False
        return True




if __name__ == "__main__":
    input_val = get_input_inf()
    controller = Controller(version=input_val[0])
    error_manager = ErrorManager()
    text = controller.check_text(input_val[1])
    if error_manager.has_error():
        output_inf(error_manager.get_error_messages_as_string())
    else:
        output_inf(text)
