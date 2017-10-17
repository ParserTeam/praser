import unittest
from print_reader import PrintReader


class TestPrintReader(unittest.TestCase):

    def setUp(self):
        self.print_reader_0 = PrintReader("", )
        self.print_reader_1 = PrintReader()
