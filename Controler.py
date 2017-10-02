from tkinter import filedialog
from PrintReader import PrintReader


class Controller:
    print_reader = None
    xml_reader = None
    view = None

    def __init__(self):
        self.view = "view"

    def check_text(self):
        # from View
        file_name = filedialog.askopenfile("r")
        text = file_name.read()
        xml_keys = {"rxbsp": ["MO", "OPCOND", "OPCONDMAP", "OMLSTAT", "RSLSTAT"]}

        self.print_reader = PrintReader(text, xml_keys)
        for subject in self.print_reader.subjects:
            self.subject_check(subject)

    def no_subjects(self):
        return self.print_reader.subjects != 0

    def subject_check(self, subject):
        table = None

        # get active keys for subject.name
        xml_active_keys = [{"OPCONDMAP": "16"}]
        table = subject.get_subject_in_table()
        for row in table.table:
            table.get_values_from_row(row, xml_active_keys)


controller = Controller()


if controller.no_subjects():
    print("Can't find eny subject to read")
    exit(0)


