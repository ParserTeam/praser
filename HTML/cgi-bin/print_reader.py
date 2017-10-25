from re import match, finditer, sub
from bscswupg_mmlparser import MMLparser

SRE_MATCH_TYPE = type(match("", ""))


class PrintReader:
    subjects = None
    text = None

    def __init__(self, text, configuration_keys):
        text += "\n" * 4
        self.text = text.replace("\r\n", "\n")
        self.subjects = self._split_text(text, configuration_keys)
        self._add_texts_to_subjects(self.subjects, self.text)

    def _split_text(self, text, configuration_keys):
        """
        :param text: input text with printouts;
        :param configuration_keys: dictionary with xml_file name as key and limiter as value
        :return: list with SubText object
        """
        result = list()

        for file_name, limiter in configuration_keys.items():
            limiter = limiter.replace(" /any/ ", r"[\s|\n][\s\S]*?")
            limiter = limiter.replace(" /or/ ", r"|")
            limiter = limiter.replace(" ", r"\s+")
            # if match("$")
            # print file_name, limiter
            texts = finditer(limiter, text)
            self._unite_texts(result, texts, file_name)
        return result

    def _unite_texts(self, result, texts, file_name):
        """
        This function add to SubText object file with overlapping
        :param result: list of SubText objects
        :param texts: list of SRE_Match objects with all printouts correspond this xml file
        :param file_name: xml file name
        """
        # i = 0
        for text in texts:
            # i += 1
            # print ("+" * 20) + str(i) + ("+" * 20)
            # print "######\n" + text.group(0) + "#########\n"
            if text in result:
                for subtext_obj in result:
                    subtext_obj.update_if_need(text, file_name)
            else:
                result += [SubText(text, file_name)]
        # print i

    def _add_texts_to_subjects(self, subjects, text):
        """
        This function add text parts to each SubText object in subjects list
        :param subjects: list of SubText objects
        :param text: all input text
        """
        for subject in subjects:
            subject.add_text(text)

    def get_check_values(self):
        subject_values = []

        for subject in self.subjects:
            subject_values += [CheckedValues(subject.parse_self(), subject.xml_file_obj)]
        return subject_values


class SubText:
    start = None
    end = None
    file_names = None
    xml_file_obj = None
    text = None

    def __init__(self, text, file_name):
        self.file_names = [file_name]
        self.start = text.start()
        self.end = text.end()

    def update_if_need(self, text, file_name):
        """
        :param text: text SRE_Match object to update
        :param file_name: name of xml file witch correspond this text
        :return: true when object was updated
        """
        # check if need update
        if text.start() < self.end and text.end() > self.start:
            self.start = text.start() if text.start() < self.start else self.start
            self.end = text.end() if text.end() > self.end else self.end
            self.file_names += [file_name]
            return True
        return False

    def add_text(self, text):
        self.text = text[self.start: self.end]

    def parse_self(self):
        self._replace_space_in_text_for_keys([key.name for key in self.xml_file_obj.list_of_object_keys])
        self.text = "\n" + self.xml_file_obj.header + "\n\n" + self.text
        return MMLparser(objIds=[self.xml_file_obj.name_key]).parsePrintouts(self.text)

    def _replace_space_in_text_for_keys(self, keys):
        for key in keys:
            pattern = key.replace("_", "\s+")
            if "_" in key:
                self.text = sub(pattern, key, self.text)

    def __eq__(self, other):
        """
        This function implement eq method
            If other object type is SRE_Match, this method check if texts is overlapping
        :param other: object to compare with
        :return: boolean
        """
        if type(other) == SRE_MATCH_TYPE:
            return other.start() < self.end and other.end() > self.start
        if type(object) == type(self):
            return self.start == other.start and self.end == other.end
        return False


class CheckedValues:
    """
    parse_objects structure:
    [{'MO': 'RXOTG-187', 'CASCADABLE': 'YES', 'OMLF1': '72DFBFFC',
    'OMLF2': 'FF', 'RSLF1': '1FFFFFFBFF', 'RSLF2': 'FF', 'FTXADDR': 'NO'}]
    """
    xml_file_name = None
    xml_obj = None
    parse_objects = None

    def __init__(self, subjects, xml_obj):
        active_keys = self._get_active_keys(xml_obj.list_of_object_keys)
        self.xml_obj = xml_obj
        self.xml_file_name = xml_obj.name_of_CANDY
        self.xml_header = xml_obj.header
        self.parse_objects = self._select_values_to_parse_objects(subjects, active_keys)

    def _select_values_to_parse_objects(self, subjects, active_keys):
        """
        This function does magic:

        :param subjects: list with dictionaries of objects
        :param active_keys: dictionary with active keys like a key and direction like value
        :return: parse_objects: list of dictionaries (main objects) with keys from printout as key and
                    values like value
        """
        parse_objects = []
        print_keys_with_val = dict()
        for subject in subjects:
            # subject:              dictionary of all keys and list of values in subject
            # name_key_values:      list of main key values, it should be added to all dictionaries
            # print_keys_with_val:  dictionary with keys and values for keys that are one for few objects
            # name_key_values_len:  number of name key values (number of objects)
            name_key_values = subject.get(self.xml_obj.name_key) or []
            print_keys_with_val = self._get_print_keys_with_val(subject, print_keys_with_val)
            name_key_values_len = len(name_key_values)

            # going through all objects in subject to collect all values from it
            for i in range(name_key_values_len):
                # my_values:    dictionary of object to return
                my_values = dict()
                my_values.update(print_keys_with_val)  # add the print key and value to each object dict

                # going through all elements in subject
                for key, val in subject.items():

                    # if key is one of active keys or object name key it will be add to dictionary
                    if key in active_keys.keys():
                        # direction:    in which direction value should be concatenate (don't concatenate for 0)
                        direction = int(active_keys.get(key) or 0)

                        my_values[key] = self._values_to_string(val, direction, name_key_values_len, i)
                    elif key == self.xml_obj.name_key:
                        my_values[key] = val[i]
                parse_objects += [my_values]
        return parse_objects

    def _get_print_keys_with_val(self, subject, print_keys_with_val):
        """
        :param subject:
        :param print_keys:
        :return:
        """
        if not self.xml_obj.list_of_keys_to_print:
            return {}
        result = dict()
        for key in self.xml_obj.list_of_keys_to_print:
            result[key] = subject.get(key) or print_keys_with_val.get(key) or '-'
        return result

    def _get_active_keys(self, list_of_object_keys):
        active_keys = dict()
        for key in list_of_object_keys:
            active_keys[key.name] = key.direction
        return active_keys

    def _values_to_string(self, values, direction, name_key_val_len, position):
        """
        Transform the value from list to string
        :param values: list of strings
        :param direction: 1 is from left to right and -1 vice versa or 0 return first element
        :param position: main object array position
        :param name_key_val_len: main object values len (to calculate
        :return: string
        """
        pattern = "H'([a-fA-F\d]+)"
        if direction == 0:
            return [sub(pattern, lambda m: m.group(1), value) for value in values]
        values = values[::direction]
        result = ""
        size = len(values) / name_key_val_len
        for i in range(position * size, position * size + size):
            result += sub(pattern, lambda m: m.group(1), values[i])
        return [result]

    def __repr__(self):
        return "CheckValue object: {}".format(self.parse_objects)
