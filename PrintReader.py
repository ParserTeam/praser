
from re import findall
from re import sub


class PrintReader:
    subjects = []

    def __init__(self, text, limiter):
        text = findall(limiter[0] + ".*?" + limiter[1], text)

        print(te)
        # for string in text:
        #     subject = self.get_subject(string, configuration_keys)
        #     if subject:
        #         self.subjects += [subject]

    def get_subject(self, line, configuration_keys):
        for subject_name, subject_values in configuration_keys.items():
            if self._all_keys_in_line(line, subject_values[0]):
                return Subject(subject_name, subject_values[1], line)
        return None

    @staticmethod
    def _all_keys_in_line(line, subject_keys):
        for key in subject_keys:
            if key not in line:
                return False
        return True


class Subject:
    file_name = None
    name = None
    text = None
    table = None

    def __init__(self, file_name, name_key, text):
        self.file_name = file_name
        self.text = text
        self.table = Table(self.text)
        self.name = self.table.get_string_by_column_name(name_key, 0)

    def has_key(self, key):
        return key in self.text

    def has_keys(self, keys):
        for key in keys:
            if key not in self.text:
                return False

    def get_subject_in_table(self):
        return self.table

    def __str__(self):
        return "Name:\n" + self.name + "\nSubject:\n" + self.text


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


