from Controler import Controller
from tkFileDialog import askopenfile
import difflib

def read_file_to(filename):
    res = ""
    with open(filename) as input_data:
        # Reads text until the end of the block:
        for line in input_data:  # This keeps reading the file
            if line.strip() == '#### expected value ####':
                break
            res += line
    return res  # Line is extracted (or block_of_lines.append(line), etc.)

def print_from_to(filename):
    data_file = open(filename)
    block = ""
    found = False

    for line in data_file:
        if found:
            block += line
            if line.strip() == "#### EOF ####":
                block = block.replace("\n#### EOF ####", "")
                break
        else:
            if line.strip() == "#### expected value ####":
                found = True
                # block = "#### expected value ####"

    data_file.close()
    return block


def compare_dictionaries(dict_1, dict_2, dict_1_name, dict_2_name, path=""):
    # type: (object, object, object, object, object) -> object
    """Compare two dictionaries recursively to find non mathcing elements

    Args:
        dict_1: dictionary 1
        dict_2: dictionary 2

    Returns:

    """
    err = ''
    key_err = ''
    value_err = ''
    old_path = path
    for k in dict_1.keys():
        path = old_path + "[%s]" % k
        if not dict_2.has_key(k):
            key_err += "Key %s%s not in %s\n" % (dict_2_name, path, dict_2_name)
        else:
            if isinstance(dict_1[k], dict) and isinstance(dict_2[k], dict):
                err += compare_dictionaries(dict_1[k],dict_2[k],'d1','d2', path)
            else:
                if dict_1[k] != dict_2[k]:
                    value_err += "Value of %s%s (%s) not same as %s%s (%s)\n"\
                        % (dict_1_name, path, dict_1[k], dict_2_name, path, dict_2[k])

    for k in dict_2.keys():
        path = old_path + "[%s]" % k
        if not dict_1.has_key(k):
            key_err += "Key %s%s not in %s\n" % (dict_2_name, path, dict_1_name)

    return key_err + value_err + err


import difflib
import pprint


def return_max(s1, s2):
    if s1 > s2:
        return s1
    else:
        return s2


if __name__ == "__main__":
    controller = Controller()
    # input_text = askopenfile("r").read()
    # result = controller.check_text(input_text)
    # print  result
    input_text = read_file_to('rxmspTest.txt')

    # print input_text
    result = controller.check_text(input_text)
    import ast
    diff = print_from_to('rxmspTest.txt')
    test = ast.literal_eval(diff)
    res_dect = ""
    # print result['rxmsp.xml']
    len_res = len(result['rxmsp.xml'])
    len_dif = len(test['rxmsp.xml'])
    if len_res > len_dif:
        len_max = result['rxmsp.xml']
    else:
        len_max = test['rxmsp.xml']

    for i in range(len_max):
        res_dect = compare_dictionaries(result[i], test[i], "dict_r", "dict_d")
        print res_dect
    cases = [(result, diff)]
    cases = [(str(result), str(diff))]

    # for a, b in cases:
    #     # print('{}\n=>\n{}'.format(a, b))
    #     container = ""
    #     for i, s in enumerate(difflib.ndiff(a, b)):
    #         if s[0] == ' ':
    #             continue
    #         elif s[0] == '-':
    #             print u'Delete "{}" from position {}'.format(s[-1], i)
    #         elif s[0] == '+':
    #             container += s
    #         print(u'Add "{}" to position {}'.format(s[-1], i))







        # File1 = open("file1", "r")
    # File2 = open("file2", "r")
    # Dict1 = File1.readlines()
    # Dict2 = File2.readlines()
    # print Dict1
    # print Dict2
    # DF = [x for x in Dict1 if x not in Dict2]
    # print DF
    # print DF[0].rstrip()

    # print t1.__eq__(t3)

