from PrintReader import PrintReader
from XmlModule import ConfigModule
from interface import get_input_inf, output_inf, DialogWindow


class Controller:
    print_reader = None
    xml_files = None
    xml_reader = None
    list_of_xml_to_use = None

    def __init__(self):
        self.xml_reader = ConfigModule()
        self.xml_files = self.xml_reader.get_keys_from_files()

    def check_text(self, print_text, list_of_xml_to_use=None):
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
        :param list_of_xml_to_use:
                You can add ass second parameter list of files to use. When program will run, it will check if this
                parameter is not None. If it's None or anything else then list you will see the pop up window witch asks
                you to select configuration file for current printout.
                If parameter is list the program will run through the list to find corresponding file for current
                printout. If program doesn't find file, it select the first version of file.
                (To use first version for all printouts, just paste an empty list for list_of_xml_to_use)
        """
        if isinstance(list_of_xml_to_use, list):
            self.list_of_xml_to_use = list_of_xml_to_use
        self.print_reader = PrintReader(print_text, self.xml_files)
        if len(self.print_reader.subjects) == 0:
            return "<b>No file found for text</b><p>Files available: " + ", ".join(self.xml_files.keys()) + "</p>"
        self._check_file_version(self.print_reader.subjects)
        list_check_values = self.print_reader.get_check_values()
        # print list_check_values
        # return []
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
                if not printout_bits.get(bits.name):
                    value = 0
                else:
                    value = int(str(printout_bits.get(bits.name)), int(bits.type))
                value_in_bits = (format(value, "0>42b"))
                value_in_bits_revers = value_in_bits[::-1]
                printout_bits[bits.name] = {}
                for i in range(0, len(value_in_bits_revers)):

                    if value_in_bits_revers[i] != str(bits.norm_val):
                        # try:
                        for value_bit in bits.dict_bits:
                            if value_bit.value == str(i):
                                printout_bits[bits.name][value_bit.name] = value_bit.text_of_bit
                                # except IndexError:
                                #             #     pass
                                # if bits.type.isalpha():
                                #     work_dict = {}
                                #     string_value = printout_bits.get(bits.name)
                                #     # work_dict =  printout_bits[bits.name]
                                #     if string_value != str(bits.norm_val):
                                #         try:
                                #             work_dict = printout_bits
                                #         except IndexError:
                                #             work_dict = {}
                                #     else:
                                #         work_dict = {}
                                #     printout_bits = work_dict
                                # printout_bits[bits.name][cheker.name].popitem(cheker.text_of_bit)
        if not printout_bits.get(bits.name):
            return {}
        else:
            return printout_bits

    def _check_file_version(self, list_ojects):
        window = DialogWindow("Select configuration file", "Please select XML file for this printout:")
        for obj in range(len(list_ojects)):
            if len(list_ojects[obj].file_names) > 1:
                if isinstance(self.list_of_xml_to_use, list):
                    self._get_file_from_file_to_use(list_ojects[obj].file_names)
                else:
                    window.get_answer(list_ojects[obj].text, list_ojects[obj].file_names)
        self.xml_reader.get_list_objects(list_ojects)

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


class ErrorManeger:
    _instance = None
    _error = False
    _error_messages = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ErrorManeger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def has_error(self):
        return self._error

    def add_error_message(self, message):
        self._error = True
        self._error_messages += [message]

    def get_error_messages_as_string(self):
        self._error = False
        return ("\n" * 2 + ("#" * 20)).join(self._error_messages)


if __name__ == "__main__":
    controller = Controller()
    input_text = get_input_inf()
    text = controller.check_text(input_text)
    output_inf(text)
