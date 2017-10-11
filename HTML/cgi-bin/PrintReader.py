
from re import match, findall, split, finditer
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
        for text in texts:
            if text in result:
                for subtext_obj in result:
                    subtext_obj.update_if_need(text, file_name)
            else:
                result += [SubText(text, file_name)]

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
        self.text = "\n" + self.xml_file_obj.header + "\n\n" + self.text
        return MMLparser().parsePrintouts(self.text)

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
        active_keys = [key.name for key in xml_obj.list_of_object_keys]
        self.xml_obj = xml_obj
        self.xml_file_name = xml_obj.name_of_CANDY
        self.parse_objects = self._select_values_to_parse_objects(subjects, active_keys)

    def _select_values_to_parse_objects(self, subjects, active_keys):
        parse_objects = []
        for subject in subjects:
            my_values = dict()
            for key, val in subject.items():
                if key in active_keys or key == self.xml_obj.name_key:
                    my_values[key] = self._values_to_string(val, -1)
            parse_objects += [my_values]
        return parse_objects

    def _values_to_string(self, values, direction):
        """
        Transform the value from list to string
        :param values: list of strings
        :param direction: 1 is from left to right and -1 vice versa
        :return: string
        """
        values = values[::direction]
        result = ""
        for value in values:
            result += value
        return result

    def __repr__(self):
        return "CheckValue object: {}".format(self.parse_objects)


        #
# class Subject:
#     xml_instance = None
#     text = None
#     tables = None
#     file_name = None
#     add_to_print = None
#
#     def __init__(self, text, xml_objects):
#         self.text = text
#         for file_name, xml_obj in xml_objects.items():
#             if match(xml_obj.root_limiter, text):
#                 self.xml_instance = xml_obj
#                 self.file_name = file_name
#                 break
#         lines = split("\n{2,}", text)
#         self.tables = []
#         self._make_tables(lines)
#         if self.xml_instance.list_of_keys_to_print:
#             self._set_add_to_print()
#
#     def _set_add_to_print(self):
#         self.add_to_print = dict()
#         table = None
#         keys = split("\s+", self.xml_instance.list_of_keys_to_print)
#
#         for key in keys:
#             table = self.get_table_by_keys([key])
#             if table:
#                 self.add_to_print[key] = table.get_value(0, key, None, None)
#
#     def get_table_by_keys(self, keys):
#         for table in self.tables:
#             if table.have_keys(keys):
#                 return table
#
#     def _make_tables(self, lines):
#         for line in lines:
#             if line:
#                 self.tables += [Table(line)]
#
#     def get_name_key(self):
#         return self.xml_instance.name_key
#
#     def has_key(self, key):
#         return key in self.text
#
#     def has_keys(self, keys):
#         for key in keys:
#             if key not in self.text:
#                 return False
#
#     def get_subject_in_table(self):
#         return self.table
#
#     def get_objects_to_check(self):
#         keys = [obj_key.name for obj_key in self.xml_instance.list_of_object_keys]
#         table = self.get_table_by_keys(keys)
#         objects = []
#         while table and not table.table_end:
#             objects += [table.get_next_row(self.xml_instance)]
#         return objects
#
#     def __str__(self):
#         return "Name:\n" + self.xml_instance.name_of_CANDY + "\nSubject:\n" + self.text
#
#     def __repr__(self):
#         return "Subject: " + self.xml_instance.name_of_CANDY
#
#
# class Table:
#     Y = 0
#     X = 1
#
#     header_row_with_start = None
#     table = None
#     current_row = 0
#     table_end = False
#
#     def __init__(self, text):
#         lines = split("\n", text)
#         self.header_row_with_start = dict()
#         self.table = []
#         self._set_header(lines[0])
#         self._set_table(lines[1:])
#
# # create table
#     def _set_header(self, line):
#         header_arr = finditer("[\w:'-]+", line)
#         for column in header_arr:
#             self.header_row_with_start[column.group(0)] = column.start()
#
#     def _set_table(self, lines):
#         for line in lines:
#             self.table += [self._make_row(line)]
#
#     def _make_row(self, line):
#         column_start = list(self.header_row_with_start.values())
#         column_start_len = len(column_start)
#         row = []
#
#         for i in range(column_start_len):
#             if i + 1 < column_start_len:
#                 cell = line[column_start[i]:column_start[i + 1]]
#             else:
#                 cell = line[column_start[i]:]
#             row += [cell.strip()]
#         return row
# # end create table
#
# # get value
#     def get_value(self, row_nbr, column, start, end):
#         column_nbr = list(self.header_row_with_start.keys()).index(column)
#         start_coor = self._coor_to_int(start or "0,0")
#         end_coor = self._coor_to_int(end or "0,0")
#         return self._value_in_column(row_nbr, column_nbr, start_coor, end_coor)
#
#     def _value_in_column(self, row, column, start, end):
#         value = ""
#         while start[self.Y] < end[self.Y]:
#             value += self._value_in_row(row, column, start, end)
#             start[self.Y] += 1
#         while start[self.Y] > end[self.Y]:
#             value += self._value_in_row(row, column, start, end)
#             start[self.Y] -= 1
#         value += self._value_in_row(row, column, start, end)
#         return value
#
#     def _value_in_row(self, row, column, start, end):
#         value = ""
#         while start[self.X] < end[self.X]:
#             value += self._get_value(column, row) or ""
#             start[self.X] += 1
#         while start[self.X] > end[self.X]:
#             value += self._get_value(column, row) or ""
#             start[self.X] -= 1
#         value += self._get_value(column + start[self.X], row + start[self.Y]) or ""
#         return value
#
#     def _get_value(self, column_nbr, row_nbr):
#         try:
#             return self.table[row_nbr][column_nbr]
#         except IndexError:
#             return None
#
#     def _coor_to_int(self, coor):
#         coor_arr = split("[\s,]+", coor)
#         return [int(coor_arr[self.Y]), int(coor_arr[self.X])]
#
# # end get value
#
#     def get_name(self):
#         return " ".join(self.header_row_with_start.keys())
#
#     def have_keys(self, keys):
#         for key in keys:
#             if key not in self.header_row_with_start.keys():
#                 return False
#         return True
#
#     def get_next_row(self, xml_obj):
#         row_nbr = self.current_row
#         self.current_row = self._get_next_row_nbr(row_nbr, xml_obj.name_key)
#         if self.current_row == row_nbr:
#             self.table_end = True
#         return self._row_to_dict(row_nbr, xml_obj.list_of_object_keys)
#
#     def _row_to_dict(self, row_nbr, list_of_obj_keys):
#         row_dict = dict()
#         for column in self.header_row_with_start.keys():
#             key_obj = self._get_key_obj(column, list_of_obj_keys)
#             if key_obj:
#                 row_dict[key_obj.name] = self.get_value(row_nbr, key_obj.name, key_obj.start, key_obj.end)
#             else:
#                 row_dict[column] = self.get_value(row_nbr, column, None, None)
#         return row_dict
#
#     def _get_key_obj(self, name, list_of_obj_keys):
#         for key_obj in list_of_obj_keys:
#             if name == key_obj.name:
#                 return key_obj
#
#     def _get_next_row_nbr(self, old_row_nbr, name_key):
#         new_row_nbr = old_row_nbr
#         column_nbr = list(self.header_row_with_start.keys()).index(name_key)
#         while new_row_nbr < len(self.table):
#             new_row_nbr += 1
#             value = self._get_value(column_nbr, new_row_nbr)
#             if value and value != "END":
#                 return new_row_nbr
#         return old_row_nbr
#
#     def __repr__(self):
#         return "Table: header = '{}'".format(self.get_name())
#
#
#