from tkinter import filedialog
from PrintReader import PrintReader
from XmlModule import ConfigModule


class Controller:
    print_reader = None
    xml_files = None
    xml_reader = None
    view = None

    def __init__(self):
        self.view = "view"
        self.xml_reader = ConfigModule()
        self.xml_files = self.xml_reader.get_dict_from_files()

    def check_text(self):
        # from View
        file_name = filedialog.askopenfile("r")
        text = file_name.read()

        self.xml_reader = ConfigModule()
        self.print_reader = PrintReader(text, self.xml_files)
        for subject in self.print_reader.subjects:
            self.subject_check(subject)

    def no_subjects(self):
        return len(self.print_reader.subjects) == 0

    def subject_check(self, subject):
        table = None

        # get active keys for subject.name
        # xml_active_keys = self.xml_reader.get_dict_with_properties(subject.file_name)
        xml_active_keys = {'OMLF1': {'type': '16', 'size_h': '2'}, 'OMLF2': '16', 'RSLF1': {'type': '16', 'size_h': '3'}, 'RSLF2': '16'}
        print(xml_active_keys)
        table = subject.get_subject_in_table()
        print(subject.file_name + ": " + subject.name)
        for row in table.table:
            print(table.get_values_from_row(row, xml_active_keys))


file_name = filedialog.askopenfile("r")
text = file_name.read()
xml_reader = ConfigModule()
print_reader = PrintReader(text, xml_reader.get_dict_from_files())



