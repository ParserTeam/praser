
from re import split


class PrintReader:
    subjects = []

    def __init__(self, text, configuration_keys):
        text = split("\n{2,}", text)

        for string in text:
            subject = self.get_subject(string, configuration_keys)
            if subject:
                self.subjects += [subject]

    def get_subject(self, line, configuration_keys):
        for subject_name, subject_keys in configuration_keys.items():
            if self._all_keys_in_line(line, subject_keys):
                return Subject(subject_name, line)
        return None

    @staticmethod
    def _all_keys_in_line(line, subject_keys):
        for key in subject_keys:
            if key not in line:
                return False
        return True


class Subject:
    name = None
    text = None

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def has_key(self, key):
        return key in self.text

    def has_keys(self, keys):
        for key in keys:
            if key not in self.text:
                return False

    def get_values_table(self):
        return self.text

    def __str__(self):
        return "Name:\n" + self.name + "\nSubject:\n" + self.text
