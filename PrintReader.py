
from re import split


class PrintReader:
    subjects = None
    current_index = 0

    def __init__(self, text):
        self.subjects = split(r"\n{2,}", text)

    def get_next_subject(self):
        subject = self.subjects[self.current_index]
        self.current_index += 1
        return subject

    def current_subject_have_key(self, key):
        return key in self.subjects[self.current_index]




if __name__ == "__main__":
    from tkinter import filedialog

    file_name = filedialog.askopenfile("r")
    text = file_name.read()
    print(text)
    print_reader = PrintReader(text)
    print_reader.get_next_subject()
