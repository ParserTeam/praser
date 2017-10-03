
from re import match, findall, split
from re import sub


class PrintReader:
    subjects = None
    xml_files = None
    key_file_patterns = None
    text = None

    def __init__(self, text, configuration_keys):
        self.subjects = []
        self.key_file_pattern = dict()
        pattern = None
        self.text = text
        for file_name, keys in configuration_keys.items():
            pattern = "[\s\S]*" + "[\s\S]*".join(keys) + "[\s\S]*"
            if match(pattern, text):
                self.key_file_pattern[file_name] = pattern

    def get_config_files_in_text(self):
        return list(self.key_file_pattern.keys())

    def make_subjects(self, xml_objects):
        limiters = [xml_obj.root_limiter for xml_obj in xml_objects.values()]
        subject_texts = findall("|".join(limiters), self.text + "\n\n")
        for sub_text in subject_texts:
            self.subjects += [Subject(sub_text, xml_objects)]


class Subject:
    xml_instance = None
    text = None
    table = None

    def __init__(self, text, xml_objects):
        self.text = text
        self.table = Table(text)
        for file_name, xml_obj in xml_objects.items():
            if match(xml_obj.root_limiter, text):
                self.xml_instance = xml_obj

    def has_key(self, key):
        return key in self.text

    def has_keys(self, keys):
        for key in keys:
            if key not in self.text:
                return False

    def get_subject_in_table(self):
        return self.table

    def __str__(self):
        return "Name:\n" + self.xml_instance.name_of_CANDY + "\nSubject:\n" + self.text

    def __repr__(self):
        return "Subject: " + self.xml_instance.name_of_CANDY


class Table:
    header_row = []
    header_index = None
    table = [[]]

    def __init__(self, text):
        lines = split("\n+", text)
        self.header_index = []
        self.header_row = self._make_header(lines[0], self.header_index)
        self.table = self._make_table(lines[1:], self.header_index)

    def _make_header(self, line, header_index):
        array = split(" +", line)

        for i in range(len(array)):
            header_index += [line.find(array[i])]
            array[i] = array[i].strip()
        return array

    def _make_table(self, lines, header_index):
        table = []

        for line in lines:
            table += [self._make_row(line, header_index)]
        return table

    def _make_row(self, line, header_index):
        row = []
        value = None
        index_len = len(header_index)
        end_i = 0

        # find columns in the row
        for i in range(index_len):
            if i < index_len - 1:
                end_i = header_index[i + 1]
            else:
                end_i = len(line)
            value = line[header_index[i]:end_i]
            row += [value.strip()]
        return row

    def get_number_of_rows(self):
        return len(self.table)

    def get_values_from_row(self, row, columns_names):
        active_val = []
        columns_num = None

        for name, value_as in columns_names.items():
            column_num = self.header_row.index(name)
            active_val += [{name: self._get_value_from(row, column_num, value_as)}]
        return active_val

    def _get_value_from(self, row, column_num, read_as):
        if read_as == "str":
            return row[column_num]
        if read_as.isdigit():
            return int(row[column_num] or "0", int(read_as))

    def get_string_by_column_name(self, name, row_num):
        column_num = self.header_row.index(name)
        return self._get_value_from(self.table[row_num], column_num, "str")



