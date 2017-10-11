from Controler import Controller
from tkFileDialog import askopenfile

if __name__ == "__main__":
    controller = Controller()
    input_text = askopenfile("r").read()
    print controller.check_text(input_text)

