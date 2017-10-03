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
        self.xml_files = self.xml_reader.get_keys_from_files()

    def check_text(self):
        # from View
        file_name = filedialog.askopenfile("r")
        text = file_name.read()

        self.xml_reader = ConfigModule()
        self.print_reader = PrintReader(text, self.xml_files)
        xml_objects = self.xml_reader.get_list_objects(self.print_reader.get_config_files_in_text())
        self.print_reader.make_subjects(xml_objects)
        # print(list)
        # for key, val in list.items():
        #     print(key + "$", val)
        # for subject in self.print_reader.subjects:
        #     self.subject_check(subject)

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


controller = Controller()

# on button click
controller.check_text()
if controller.no_subjects():
    print("Can't find eny subject to read")
    exit(0)
# end on button click

