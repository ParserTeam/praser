import unittest
import re
from xml_module import ConfigModule
from print_reader import SubText


list_file_names_rxbsp = ["rxbsp.xml"]
list_file_names_rrscp = ["rrscp.xml"]
list_file_names_rxcap = ["rxcap.xml"]
list_file_names_rrbvp = ["rrbvp.xml"]
list_file_names_rxmsp = ["rxmsp.xml"]
list_file_names_rxmfp = ["rxmfp.xml"]
# list_file_names_rxbsp = ["rxbsp.xml"]





get_keys_from_files_expected_A58 = {'rrbvp.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}',
                                    'rrscp.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}',
                                    'rxmsp.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                    'rxbsp.xml': 'MO OPCOND OPCONDMAP OMLSTAT RSLSTAT /any/ \\n{2,}',
                                    'rxcap.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA TCFMODE TCHMODE /any/ \\n{2,} /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \\n{2,}'}

get_keys_from_files_expected_A57 ={'rrbvp.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}',
                                   'rxmsp.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                   'rxbsp.xml': 'MO OPCOND OPCONDMAP OMLSTAT RSLSTAT /any/ \\n{2,}',
                                   'rxcap.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA TCFMODE TCHMODE /any/ \\n{2,} /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \\n{2,}',
                                   'rxmfp.xml': 'MO BTSSWVER /any/ FAULT CODES CLASS 2A /any/ \\n{2,}',
                                   'rrscp.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}'}


get_keys_from_files_expected_A56 = {'rrbvp_ver1.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}',
                                    'rxmsp.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                    'rxbsp_ver1.xml': 'MO OPCOND OPCONDMAP OMLSTAT RSLSTAT /any/ CNFG /any/ \\n{2,}',
                                    'rxcap.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA TCFMODE TCHMODE /any/ \\n{2,} /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \\n{2,}',
                                    'rrscp_ver1.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}'}

get_keys_from_files_expected_A55 = {'rrbvp_ver1.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}',
                                    'rxmsp.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                    'rxbsp_ver1.xml': 'MO OPCOND OPCONDMAP OMLSTAT RSLSTAT /any/ CNFG /any/ \\n{2,}',
                                    'rxcap.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA TCFMODE TCHMODE /any/ \\n{2,} /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \\n{2,}',
                                    'rrscp_ver1.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}'}

get_keys_from_files_expected_A54 = {'rrbvp_ver1.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}',
                                     'rxmsp.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                     'rxbsp_ver1.xml': 'MO OPCOND OPCONDMAP OMLSTAT RSLSTAT /any/ CNFG /any/ \\n{2,}',
                                     'rxcap_ver2.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA TCFMODE TCHMODE /any/ \\n{2,} /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \\n{2,}',
                                     'rrscp_ver1.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}'}

get_keys_from_files_expected_A53 = {'rrbvp_ver1.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}',
                                    'rxcap_ver1.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA TCFMODE TCHMODE /any/ \\n{2,} /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \\n{2,}',
                                    'rxmsp.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                    'rrscp_ver1.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}'}

get_keys_from_files_expected_G14B ={'rrbvp_ver1.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}',
                                    'rrscp_ver2.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}',
                                    'rxmsp_ver1.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                    'rxcap_ver4.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA TCFMODE TCHMODE /any/ \\n{2,} /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \\n{2,}'}

get_keys_from_files_expected_G13B = {'rrscp_ver3.xml': 'SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \\n{2,}',
                                     'rxcap_ver3.xml': 'MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \\n{2,} /any/ AA\\s+TCFMODE\\s+TCHMODE \\n{2,}|MO\\s+CASCADABLE\\s+OMLF1\\s+OMLF2\\s+RSLF1\\s+RSLF2\\s+FTXADDR \\n{2,}',
                                     'rxmsp_ver1.xml': 'MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \\n{2,}',
                                     'rrbvp_ver2.xml': 'NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \\n{2,}'}


class Test_xml_module(unittest.TestCase):

    def setUp(self):
        self.xml_module_A58 = ConfigModule("A58")
        self.xml_module_A57 = ConfigModule("A57")
        self.xml_module_A56 = ConfigModule("A56")
        self.xml_module_A55 = ConfigModule("A55")
        self.xml_module_A54 = ConfigModule("A54")
        self.xml_module_A53 = ConfigModule("A53")
        self.xml_module_G14B = ConfigModule("G14B")
        self.xml_module_G13B = ConfigModule("G13B")

    def _create_out_get_list(self):
        pass

    def _create_sub_text_object(self):

        self.subject = SubText(re.match("",""), list_file_names_rxbsp)
        self.subject.file_name = list_file_names_rxbsp[0]
        return self.subject

    # def test_get_list_objects(self):
    #     self.assertEqual(self.xml_module_A57.get_list_objects([self._create_sub_text_object()]),"1212")


    def _my_assert(self, my_val, expected_val, *args):
        self.assertEqual(my_val, expected_val, args[0].format(my_val, expected_val, *args[1:]))


    def test_get_keys_from_files(self):
        message = "Something wrong"
        self.assertEqual(self.xml_module_A58.get_keys_from_files(), get_keys_from_files_expected_A58)
        self.assertEqual(self.xml_module_A57.get_keys_from_files(), get_keys_from_files_expected_A57)
        self.assertEqual(self.xml_module_A56.get_keys_from_files(), get_keys_from_files_expected_A56)
        self.assertEqual(self.xml_module_A55.get_keys_from_files(), get_keys_from_files_expected_A55)
        self.assertEqual(self.xml_module_A54.get_keys_from_files(), get_keys_from_files_expected_A54)
        self.assertEqual(self.xml_module_A53.get_keys_from_files(), get_keys_from_files_expected_A53)
        self.assertEqual(self.xml_module_G14B.get_keys_from_files(), get_keys_from_files_expected_G14B)
        self.assertEqual(self.xml_module_G13B.get_keys_from_files(), get_keys_from_files_expected_G13B)

    # def test_get_list_objects(self):
    #     pass
    #
    #     # self.assertEqual(self.xml_module_A57.get_list_objects(),)


if __name__ == '__main__':
    unittest.main(exit=False)