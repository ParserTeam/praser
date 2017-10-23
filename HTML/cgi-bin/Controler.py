from print_reader import PrintReader
from xml_module import ConfigModule
from interface import get_input_inf, output_inf, DialogWindow
from ErrorManager import ErrorManager


class Controller:
    print_reader = None
    xml_files = None
    xml_reader = None
    list_of_xml_to_use = None

    def __init__(self, version=None):
        if version is None:
            version = "A57"
        self.xml_reader = ConfigModule(version)
        self.xml_files = self.xml_reader.get_keys_from_files()
        for key, val in self.xml_files.items():
            if "Wrong xml file: " in val:
                error_manager.add_error_message(val + key)

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
        self._check_file_version(self.print_reader.subjects)
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
        if not result:
            return "<strong>All values is in default state!</strong>"
        return result

    def _valid_printout_bits(self, number, in_type, out_type):

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
                        value = self._valid_printout_bits(bits_name_value, bits.in_type, bits.out_type)

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

        if self._is_all_values_is_empty(printout_bits, config_bits):
            return {}
        else:
            return printout_bits

    def _is_all_values_is_empty(self, printout_bits, config_bits):
        for key, val in printout_bits.items():
            if key != config_bits.name_key and key not in config_bits.list_of_keys_to_print:
                if val:
                    return False
        return True

    def _check_file_version(self, list_objects):
        window = DialogWindow("Select configuration file", "Please select XML file for this printout:")
        for obj in range(len(list_objects)):
            if len(list_objects[obj].file_names) > 1:
                if isinstance(self.list_of_xml_to_use, list):
                    list_objects[obj].file_name = self._get_file_from_file_to_use(list_objects[obj].file_names)
                else:
                    list_objects[obj].file_name = window.get_answer(list_objects[obj].text, list_objects[obj].file_names)
            else:
                list_objects[obj].file_name = list_objects[obj].file_names[0]
        self.xml_reader.get_list_objects(list_objects)

    def _get_file_from_file_to_use(self, ask_files):
        for file_to_use in self.list_of_xml_to_use:
            for ask_file in ask_files:
                # to insure that filename have .xml extension
                file_to_use = file_to_use.replace(".xml", "")
                file_to_use += ".xml"
                if ask_file == file_to_use:
                    return ask_file
        ask_files.sort()
        return ask_files[0]


if __name__ == "__main__":
    error_manager = ErrorManager()
    input_val = get_input_inf()
    controller = Controller(version=input_val[0])
    text = controller.check_text(input_val[1])
    output_inf(text, error_manager.get_error_messages_as_string())
