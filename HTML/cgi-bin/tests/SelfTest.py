from Controler import Controller
from tkFileDialog import askopenfile


class TestTextReader:
    TEST_DIRECTORY = './'

    def __init__(self):



if __name__ == "__main__":
    controller = Controller()
    input_text = askopenfile("r").read()
    result = controller.check_text(input_text)

