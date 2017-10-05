
from re import match, findall, split, finditer
from os import linesep


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
        subject_texts = findall("|".join(limiters), self.text + (linesep * 2))
        for sub_text in subject_texts:
            self.subjects += [Subject(sub_text, xml_objects)]

    def get_check_values(self):
        subject_values = []

        for subject in self.subjects:
            subject_values += [CheckedValues(subject)]
        return subject_values


class Subject:
    xml_instance = None
    text = None
    tables = None
    file_name = None
    add_to_print = None

    def __init__(self, text, xml_objects):
        self.text = text
        for file_name, xml_obj in xml_objects.items():
            if match(xml_obj.root_limiter, text):
                self.xml_instance = xml_obj
                self.file_name = file_name
                break
        lines = split("\n{2,}", text)
        self.tables = []
        self._make_tables(lines)
        if self.xml_instance.list_of_keys_to_print:
            self._set_add_to_print()

    def _set_add_to_print(self):
        self.add_to_print = dict()
        table = None
        keys = split("\s+", self.xml_instance.list_of_keys_to_print)

        for key in keys:
            table = self.get_table_by_keys([key])
            if table:
                self.add_to_print[key] = table.get_value(0, key, None, None)

    def get_table_by_keys(self, keys):
        for table in self.tables:
            if table.have_keys(keys):
                return table

    def _make_tables(self, lines):
        for line in lines:
            if line:
                self.tables += [Table(line)]

    def get_name_key(self):
        return self.xml_instance.name_key

    def has_key(self, key):
        return key in self.text

    def has_keys(self, keys):
        for key in keys:
            if key not in self.text:
                return False

    def get_subject_in_table(self):
        return self.table

    def get_objects_to_check(self):
        keys = [obj_key.name for obj_key in self.xml_instance.list_of_object_keys]
        table = self.get_table_by_keys(keys)
        objects = []

        while not table.table_end:
            objects += [table.get_next_row(self.xml_instance)]
        return objects

    def __str__(self):
        return "Name:\n" + self.xml_instance.name_of_CANDY + "\nSubject:\n" + self.text

    def __repr__(self):
        return "Subject: " + self.xml_instance.name_of_CANDY


class Table:
    Y = 0
    X = 1

    header_row_with_start = None
    table = None
    current_row = 0
    table_end = False

    def __init__(self, text):
        lines = split("\n", text)
        self.header_row_with_start = dict()
        self.table = []
        self._set_header(lines[0])
        self._set_table(lines[1:])

# create table
    def _set_header(self, line):
        header_arr = finditer("[\w:'-]+", line)
        for column in header_arr:
            self.header_row_with_start[column.group(0)] = column.start()

    def _set_table(self, lines):
        for line in lines:
            self.table += [self._make_row(line)]

    def _make_row(self, line):
        column_start = list(self.header_row_with_start.values())
        column_start_len = len(column_start)
        row = []

        for i in range(column_start_len):
            if i + 1 < column_start_len:
                cell = line[column_start[i]:column_start[i + 1]]
            else:
                cell = line[column_start[i]:]
            row += [cell.strip()]
        return row
# end create table

# get value
    def get_value(self, row_nbr, column, start, end):
        column_nbr = list(self.header_row_with_start.keys()).index(column)
        start_coor = self._coor_to_int(start or "0,0")
        end_coor = self._coor_to_int(end or "0,0")
        return self._value_in_column(row_nbr, column_nbr, start_coor, end_coor)

    def _value_in_column(self, row, column, start, end):
        value = ""
        while start[self.Y] < end[self.Y]:
            value += self._value_in_row(row, column, start, end)
            start[self.Y] += 1
        while start[self.Y] > end[self.Y]:
            value += self._value_in_row(row, column, start, end)
            start[self.Y] -= 1
        value += self._value_in_row(row, column, start, end)
        return value

    def _value_in_row(self, row, column, start, end):
        value = ""
        while start[self.X] < end[self.X]:
            value += self._get_value(column, row) or ""
            start[self.X] += 1
        while start[self.X] > end[self.X]:
            value += self._get_value(column, row) or ""
            start[self.X] -= 1
        value += self._get_value(column + start[self.X], row + start[self.Y]) or ""
        return value

    def _get_value(self, column_nbr, row_nbr):
        try:
            return self.table[row_nbr][column_nbr]
        except IndexError:
            return None

    def _coor_to_int(self, coor):
        coor_arr = split("[\s,]+", coor)
        return [int(coor_arr[self.Y]), int(coor_arr[self.X])]

# end get value

    def get_name(self):
        return " ".join(self.header_row_with_start.keys())

    def have_keys(self, keys):
        for key in keys:
            if key not in self.header_row_with_start.keys():
                return False
        return True

    def get_next_row(self, xml_obj):
        row_nbr = self.current_row
        self.current_row = self._get_next_row_nbr(row_nbr, xml_obj.name_key)
        if self.current_row == row_nbr:
            self.table_end = True
        return self._row_to_dict(row_nbr, xml_obj.list_of_object_keys)

    def _row_to_dict(self, row_nbr, list_of_obj_keys):
        row_dict = dict()
        for column in self.header_row_with_start.keys():
            key_obj = self._get_key_obj(column, list_of_obj_keys)
            if key_obj:
                row_dict[key_obj.name] = self.get_value(row_nbr, key_obj.name, key_obj.start, key_obj.end)
            else:
                row_dict[column] = self.get_value(row_nbr, column, None, None)
        return row_dict

    def _get_key_obj(self, name, list_of_obj_keys):
        for key_obj in list_of_obj_keys:
            if name == key_obj.name:
                return key_obj

    def _get_next_row_nbr(self, old_row_nbr, name_key):
        new_row_nbr = old_row_nbr
        column_nbr = list(self.header_row_with_start.keys()).index(name_key)
        while new_row_nbr < len(self.table):
            new_row_nbr += 1
            value = self._get_value(column_nbr, new_row_nbr)
            if value and value != "END":
                return new_row_nbr
        return old_row_nbr

    def __repr__(self):
        return "Table: header = '{}'".format(self.get_name())


class CheckedValues:
    xml_file_name = None
    xml_obj = None
    add_to_print = None
    parse_objects = None

    def __init__(self, subject):
        self.xml_file_name = subject.file_name
        self.add_to_print = subject.add_to_print
        self.parse_objects = subject.get_objects_to_check()
        self.xml_obj = subject.xml_instance

    def __repr__(self):
        return "CheckValue object: {}".format(self.parse_objects)
