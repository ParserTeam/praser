import unittest
from print_reader import PrintReader
from XmlModule import ConfigObject, KeysObject

CONFIGURATION_KEYS = {
    "rxbsp.xml": "MO OPCOND OPCONDMAP OMLSTAT RSLSTAT /any/ \n{2,}",
    "rxcap.xml": "MO TEI DCP1 DCP2 OMLF1 OMLF2 RSLF1 RSLF2 /any/ \n{2,} /any/ AA TCFMODE TCHMODE  /any/ \n{2,}"
                 " /or/ MO CASCADABLE OMLF1 OMLF2 RSLF1 RSLF2 FTXADDR /any/ \n{2,}",
    "rxmfp.xml": "MO /any/ FAULT CODES CLASS 2A /any/ \n{2,}",
    "rxmsp.xml": "MO STATE BLSTATE BLO BLA LMO BTS CONF /any/ \n{2,}",
    "rrscp.xml": "SCGR SC DEV DEV1 NUMDEV DCP STATE REASON /any/ \n{2,}",
    "rrbvp.xml": "NSEI /any/ SIGBVCSTATE SGSNFEAT /any/ \n{2,}"
}

rxbsp = """
<rxbsp:mo=rxstf-200;

RADIO X-CEIVER ADMINISTRATION BTS STATUS DATA

MO               OPCOND  OPCONDMAP                      OMLSTAT  RSLSTAT
RXSTF-200        NOP     04

                 OPCONDTXT
                 nope

                 BTSSWVER         SECTOR

                 IDENTITYTXT

                 SECTORIDTXT

                 BSCDATE          BSCTIME

                 BTSDATE          BTSTIME

                 NEGA  NEGO  BTSC  BSCC  CTSN

                 CNFG  BUND  BTSN  BSCN
                 0001

END

MO               OPCOND  OPCONDMAP                      OMLSTAT  RSLSTAT
RXSTF-200        NOP     

                 OPCONDTXT
                 nope

                 BTSSWVER         SECTOR

                 IDENTITYTXT

                 SECTORIDTXT

                 BSCDATE          BSCTIME

                 BTSDATE          BTSTIME

                 NEGA  NEGO  BTSC  BSCC  CTSN

                 CNFG  BUND  BTSN  BSCN
                 0001
                 
MO               OPCOND  OPCONDMAP                      OMLSTAT  RSLSTAT
RXSTF-200        NOP     ff

                 OPCONDTXT
                 nope

                 BTSSWVER         SECTOR

                 IDENTITYTXT

                 SECTORIDTXT

                 BSCDATE          BSCTIME

                 BTSDATE          BTSTIME

                 NEGA  NEGO  BTSC  BSCC  CTSN

                 CNFG  BUND  BTSN  BSCN
                 0001
"""

rxbsp_param = {
    "name_key": "MO",
    "header": "RADIO X-CEIVER ADMINISTRATION BTS STATUS DATA",
    "list_of_keys_to_print": [],
    "list_of_object_keys": {"OPCONDMAP": 0}
}

rxbsp_expected = [
    [{'MO': 'RXSTF-200', 'OPCONDMAP': ['04']}],
    [{'MO': 'RXSTF-200'}],
    [{'MO': 'RXSTF-200', 'OPCONDMAP': ['ff']}]
]

rxcap = """
MO                CASCADABLE  OMLF1  OMLF2  RSLF1  RSLF2  FTXADDR
RXOTG-187         YES         FF      FF0   FBFF     FF   NO
                                        0   FFFF      0
                                        0     1F      0
                                        0      0      0
                                        0      0      0

MO                EXTAL
RXOCF-187         0000000000000000

                  TRU  TEI  64KCAP  DCPGROUP  DCP1  DCP2  CIS  CIT
                   0    0   YES      0        178   179   4    4
                                                    180        4
                                                    181        4
                                                    182        4
                                                    183        4
                                                    184        4
                                                    185        4
                                                    186        4

                       TRTYPE  MCTRNSUP
                       ISCTR

                  TRU  TEI  64KCAP  DCPGROUP  DCP1  DCP2  CIS  CIT
                   1    1   YES      1        187   188   4    4
                                                    189        4
                                                    190        4
                                                    191        4
                                                    192        4
                                            
                  572  573  574  575  576  577
                  578  579  580  581

MO                TEI  DCP1  DCP2  OMLF1  OMLF2  RSLF1  RSLF2
RXOTRX-187-0       0   178   179   FFDC     FF   FBFF     FF
                             180   72FF      0   FFFF      0
                             181      0      0     1F      0
                             182      0      0      0      0
                             183      0      0      0      0
                             184
                             185
                             186

                  AA   TCFMODE                TCHMODE
                  ON    0   1   2   3          0   1   2   3
                        4   5   6   7          4   5   6   7
                        8   9  10  11          8   9  10  11
                       12  13  14  15         12  13  14  15
                       16  17  18  19         16  17
                       20  21  22  23
                       24  25  26  27
                       28  29  30  31
                       32  33  34  35
                       36  37  38  39
                       40  41  42  43
                       44  45

                  DCPGROUP  IRCAP          TRTYPE  MCTRNSUP
                   0        SUPPORTED      ISC
                   
MO                CASCADABLE  OMLF1  OMLF2  RSLF1  RSLF2  FTXADDR
RXOTG-187         YES

MO                CASCADABLE  OMLF1  OMLF2  RSLF1  RSLF2  FTXADDR
RXOTG-187         YES                 FF

MO                TEI  DCP1  DCP2  OMLF1  OMLF2  RSLF1  RSLF2
RXOTRX-187-0       0   178   179   FFFF     FF   FFFF     FF
                             180   FFFF      0   FFFF      0
                             181      0      0     1F      0
                             182      0      0      0      0
                             183      0      0      0      0
                             184
                             185
                             186

                  AA   TCFMODE                TCHMODE
                  ON    0

MO                CASCADABLE  OMLF1  OMLF2  RSLF1  RSLF2  FTXADDR
RXOTG-187         YES         FF      FFFF  FFFF     FF   NO
                                        0   FFFF      0
                                        0     FF
 
"""


rxcap_param = {
    "name_key": "MO",
    "header": "RADIO X-CEIVER ADMINISTRATION",
    "list_of_keys_to_print": [],
    "list_of_object_keys": {'OMLF2': '-1', 'OMLF1': '-1', 'TCHMODE': '0', 'TCFMODE': '0', 'RSLF1': '-1'}
}

rxcap_expected = [
    [{'OMLF2': ['0000FF0'], 'MO': 'RXOTG-187', 'OMLF1': ['FF'], 'RSLF1': ['001FFFFFFBFF']}],
    [{'MO': 'RXOTRX-187-0',
      'TCHMODE': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17'],
      'OMLF2': ['0000FF'], 'OMLF1': ['00072FFFFDC'], 'RSLF1': ['001FFFFFFBFF'],
      'TCFMODE': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
                  '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34',
                  '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45']}],
    [{'MO': 'RXOTG-187'}],
    [{'OMLF2': ['FF'], 'MO': 'RXOTG-187'}],
    [{'TCFMODE': ['0'], 'OMLF2': ['0000FF'], 'MO': 'RXOTRX-187-0', 'OMLF1': ['000FFFFFFFF'], 'RSLF1': ['001FFFFFFFFF']}],
    [{'OMLF2': ['00FFFF'], 'MO': 'RXOTG-187', 'OMLF1': ['FF'], 'RSLF1': ['FFFFFFFFFF']}]
]

rxmfp = """
<rxmfp:mo=rxotg-187,subord,faulty;

RADIO X-CEIVER ADMINISTRATION
MANAGED OBJECT FAULT INFORMATION

MO                   BTSSWVER          
RXORX-187-0          ERA-G07-R37-V01

RU  RUREVISION                           RUSERIALNO
 0

    RUPOSITION                           RULOGICALID
    

    RULOGICALIDEXT


STATE  BLSTATE  INTERCNT  CONCNT  CONERRCNT  LASTFLT   LFREASON
OPER            00000                                   

FAULT CODES CLASS 2A
  1   2   3   4

END

MO                   BTSSWVER          
RXORX-187-0          ERA-G07-R37-V01

RU  RUREVISION                           RUSERIALNO
 0

    RUPOSITION                           RULOGICALID
    

    RULOGICALIDEXT


STATE  BLSTATE  INTERCNT  CONCNT  CONERRCNT  LASTFLT   LFREASON
OPER            00000                                   

FAULT CODES CLASS 2A
  0

MO                   BTSSWVER          
RXORX-187-0          ERA-G07-R37-V01

RU  RUREVISION                           RUSERIALNO
 0

    RUPOSITION                           RULOGICALID
    

    RULOGICALIDEXT


STATE  BLSTATE  INTERCNT  CONCNT  CONERRCNT  LASTFLT   LFREASON
OPER            00000                                   

FAULT CODES CLASS 2A


MO                   BTSSWVER          
RXORX-187-0          ERA-G07-R37-V01

RU  RUREVISION                           RUSERIALNO
 0

OPER            00000                                   

FAULT CODES CLASS 2A
  1   2   3   4 5 6 


MO                   BTSSWVER          
RXORX-187-0          ERA-G07-R37-V01

RU  RUREVISION                           RUSERIALNO
 0

    RUPOSITION                           RULOGICALID
    

    RULOGICALIDEXT


STATE  BLSTATE  INTERCNT  CONCNT  CONERRCNT  LASTFLT   LFREASON
OPER            00000                                   

FAULT CODES CLASS 2A
  1   2   3   4 8  9
"""

rxmfp_param = {
    "name_key": "MO",
    "header": "RADIO X-CEIVER ADMINISTRATION",
    "list_of_keys_to_print": [],
    "list_of_object_keys": {'FAULT_CODES_CLASS_2A': None}
}

rxmfp_expected = [
    [{'MO': 'RXORX-187-0', 'FAULT_CODES_CLASS_2A': ['1', '2', '3', '4']}],
    [{'MO': 'RXORX-187-0', 'FAULT_CODES_CLASS_2A': ['0']}],
    [{'MO': 'RXORX-187-0'}],
    [{'MO': 'RXORX-187-0', 'FAULT_CODES_CLASS_2A': ['1', '2', '3', '4', '5', '6']}],
    [{'MO': 'RXORX-187-0', 'FAULT_CODES_CLASS_2A': ['1', '2', '3', '4', '8', '9']}]
]

rxmsp = """
<rxmsp:mo=rxotg-187,subord;

RADIO X-CEIVER ADMINISTRATION
MANAGED OBJECT STATUS

MO               STATE  BLSTATE    BLO   BLA   LMO    BTS   CONF
RXOTG-187        OPER              0000  0000         STA
RXOCF-187        OPER              0000  0000         STA
RXOIS-187        OPER              0000  0000         DIS   CONF
RXOCON-187       OPER              0000  0000         DIS   CONF
RXOTRX-187-0     OPER              0000  0000         STA
RXORX-187-0      OPER              0000  0000  0000   ENA   ENA
RXOTS-187-0-0    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-0-1    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-0-2    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-0-3    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-0-4    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-0-5    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-0-6    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-0-7    OPER              0000  0000  0840   DIS   UNCONF
RXOTX-187-0      OPER              0000  0000  0040   DIS   UNCONF
RXOTRX-187-1     OPER              0000  0000         STA
RXORX-187-1      OPER              0000  0000  0000   ENA   ENA
RXOTS-187-1-0    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-1-1    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-1-2    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-1-3    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-1-4    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-1-5    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-1-6    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-1-7    OPER              0000  0000  0840   DIS   UNCONF
RXOTX-187-1      OPER              0000  0000  0040   DIS   UNCONF
RXOTRX-187-2     COM    MBL        0000  0002         STA
RXORX-187-2      COM    MBL        0010  0002  0140   DIS   UNCONF
RXOTS-187-2-0    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTS-187-2-1    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTS-187-2-2    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTS-187-2-3    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTS-187-2-4    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTS-187-2-5    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTS-187-2-6    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTS-187-2-7    COM    MBL        0010  0202  0940   DIS   UNCONF
RXOTX-187-2      COM    MBL        0010  0002  0140   DIS   UNCONF
RXOTRX-187-3     OPER              0000  0000         STA
RXORX-187-3      OPER              0000  0000  0000   ENA   ENA
RXOTS-187-3-0    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-3-1    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-3-2    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-3-3    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-3-4    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-3-5    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-3-6    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-3-7    OPER              0000  0000  0840   DIS   UNCONF
RXOTX-187-3      OPER              0000  0000  0040   DIS   UNCONF
RXOTRX-187-4     OPER              0000  0000         STA
RXORX-187-4      OPER              0000  0000  0000   ENA   ENA
RXOTS-187-4-0    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-4-1    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-4-2    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-4-3    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-4-4    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-4-5    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-4-6    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-4-7    OPER              0000  0000  0840   DIS   UNCONF
RXOTX-187-4      OPER              0000  0000  0040   DIS   UNCONF
RXOTRX-187-5     OPER              0000  0000         STA
RXORX-187-5      OPER              0000  0000  0000   ENA   ENA
RXOTS-187-5-0    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-5-1    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-5-2    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-5-3    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-5-4    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-5-5    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-5-6    OPER              0000  0000  0840   DIS   UNCONF
RXOTS-187-5-7    OPER              0000  0000  0840   DIS   UNCONF
RXOTX-187-5      OPER              0000  0000  0040   DIS   UNCONF
RXOTF-187        OPER              0000  0000  0000   ENA   ENA
RXODP-187-0      OPER              0000  0000         ENA   ENA

END   

MO               STATE  BLSTATE    BLO   BLA   LMO    BTS   CONF
RXOTG-187        OPER              0000  0000         STA
RXOCF-187        OPER              0000  0000         STA


MO               STATE  BLSTATE    BLO   BLA   LMO    BTS   CONF
RXOTG-187        OPER                                 STA
RXOCF-187        OPER              0000  0000         STA

MO               STATE  BLSTATE    BLO   BLA   LMO    BTS   CONF
RXOTG-187        OPER              FFFF  FFFF  FFFF   STA
RXOCF-187        OPER              0000  0000         STA



RXOTF-187        OPER              0000  0000  0000   ENA   ENA
RXODP-187-0      OPER              0000  0000         ENA   ENA
"""

rxmsp_param = {
    "name_key": "MO",
    "header": "RADIO X-CEIVER ADMINISTRATION MANAGED OBJECT STATUS",
    "list_of_keys_to_print": [],
    "list_of_object_keys": {'BLO': None, 'BLA': None, 'LMO': None}
}

rxmsp_expected = [
    [{'MO': 'RXOTG-187', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXOCF-187', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXOIS-187', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXOCON-187', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXOTRX-187-0', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXORX-187-0', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0000']}, {'MO': 'RXOTS-187-0-0', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-0-1', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-0-2', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-0-3', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-0-4', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-0-5', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-0-6', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-0-7', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTX-187-0', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0040']}, {'MO': 'RXOTRX-187-1', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXORX-187-1', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0000']}, {'MO': 'RXOTS-187-1-0', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-1-1', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-1-2', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-1-3', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-1-4', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-1-5', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-1-6', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-1-7', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTX-187-1', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0040']}, {'MO': 'RXOTRX-187-2', 'BLA': ['0002'], 'BLO': ['0000']}, {'MO': 'RXORX-187-2', 'BLA': ['0002'], 'BLO': ['0010'], 'LMO': ['0140']}, {'MO': 'RXOTS-187-2-0', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTS-187-2-1', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTS-187-2-2', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTS-187-2-3', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTS-187-2-4', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTS-187-2-5', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTS-187-2-6', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTS-187-2-7', 'BLA': ['0202'], 'BLO': ['0010'], 'LMO': ['0940']}, {'MO': 'RXOTX-187-2', 'BLA': ['0002'], 'BLO': ['0010'], 'LMO': ['0140']}, {'MO': 'RXOTRX-187-3', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXORX-187-3', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0000']}, {'MO': 'RXOTS-187-3-0', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-3-1', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-3-2', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-3-3', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-3-4', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-3-5', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-3-6', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-3-7', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTX-187-3', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0040']}, {'MO': 'RXOTRX-187-4', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXORX-187-4', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0000']}, {'MO': 'RXOTS-187-4-0', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-4-1', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-4-2', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-4-3', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-4-4', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-4-5', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-4-6', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-4-7', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTX-187-4', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0040']}, {'MO': 'RXOTRX-187-5', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXORX-187-5', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0000']}, {'MO': 'RXOTS-187-5-0', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-5-1', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-5-2', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-5-3', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-5-4', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-5-5', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-5-6', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTS-187-5-7', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0840']}, {'MO': 'RXOTX-187-5', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0040']}, {'MO': 'RXOTF-187', 'BLA': ['0000'], 'BLO': ['0000'], 'LMO': ['0000']}, {'MO': 'RXODP-187-0', 'BLA': ['0000'], 'BLO': ['0000']}],
    [{'MO': 'RXOTG-187', 'BLA': ['0000'], 'BLO': ['0000']}, {'MO': 'RXOCF-187', 'BLA': ['0000'], 'BLO': ['0000']}],
    [{'MO': 'RXOTG-187'}, {'MO': 'RXOCF-187', 'BLA': ['0000'], 'BLO': ['0000']}],
    [{'MO': 'RXOTG-187', 'BLA': ['FFFF'], 'BLO': ['FFFF'], 'LMO': ['FFFF']}, {'MO': 'RXOCF-187', 'BLA': ['0000'], 'BLO': ['0000']}]
]

rrscp = """
<rrscp:scgr=all;
RADIO TRANSMISSION SUPER CHANNEL DATA

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  20  0                  ETM4-129       31        1  FLT    H'0800 0000
      1                  ETM4-472        8       56  FLT    H'0800 0000

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  21  0                  ETM4-161       31        1  FLT    H'0800 0000

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  22  0                  ETM4-193       31        1  WO     

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  23  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  24  0                  ETM4-225       31        1  FLT    H'0800 0000
      1                  ETM4-257        8       33  FLT    H'0800 0000

END









<rrscp:scgr=all;
RADIO TRANSMISSION SUPER CHANNEL DATA

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  20  0   RTPGD-1440     RBLT2-129      31        1  WO
      1   RTPGD-1143     RBLT2-472       8       56  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  23  0   RTPGD-1408     RBLT2-225      31        1  WO
      1   RTPGD-1111     RBLT2-257       8       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  25  0   RTPGD-1376     RBLT2-297      23        9  WO
      1   RTPGD-1120     RBLT2-321      23       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  30  0   RTPGD-1344     RBLT2-449      23        1  WO
      1   RTPGD-1088     RBLT2-481      23       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  40  0   RTPGD-1312     RBLT2-513      31        1  WO
      1   RTPGD-1079     RBLT2-856       8       56  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  43  0   RTPGD-1280     RBLT2-609      31        1  WO
      1   RTPGD-1048     RBLT2-641       8       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  45  0   RTPGD-1248     RBLT2-681      23        9  WO
      1   RTPGD-1056     RBLT2-705      23       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  50  0   RTPGD-1216     RBLT2-833      23        1  WO
      1   RTPGD-1025     RBLT2-865      23       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  60  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  61  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  62  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  63  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  64  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  65  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  66  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  67  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  68  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  69  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  70  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 500  0   RTPGD-1184     RBLT2-1        31        1  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 506  0   RTPGD-1504     RBLT2-3201     31        1  WO
      1   RTPGD-1472     RBLT2-3233     31       33  WO
      2   RTPGD-1152     RBLT2-3265     31      287  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 509  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 510  0                                 31        1

END


SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 510  2


SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 510  0                                 31        1


SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  20  0                  ETM4-129       31        1  FLT    8
      1                  ETM4-472        8       56  FLT    H'0800 0000

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  20  0                  ETM4-129       31        1  FLT    H'FFFF FFFF
      1                  ETM4-472        8       56  FLT    H'0000 0000

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
      0                  ETM4-129       31        1  FLT    H'FFFF FFFF
      1                  ETM4-472        8       56  FLT    H'0000 0000

"""

rrscp_param = {
    "name_key": "SC",
    "header": "RADIO TRANSMISSION SUPER CHANNEL DATA",
    "list_of_keys_to_print": ['SCGR'],
    "list_of_object_keys": {'REASON': '1'}
}

rrscp_expected = [
    [{'SC': '0', 'REASON': ['08000000'], 'SCGR': ['20']}, {'SC': '1', 'REASON': ['08000000'], 'SCGR': ['20']}],
    [{'SC': '0', 'REASON': ['08000000'], 'SCGR': ['21']}],
    [{'SC': '0', 'SCGR': ['22']}],
    [{'SC': '0', 'SCGR': ['23']}, {'SC': '1', 'SCGR': ['23']}, {'SC': '2', 'SCGR': ['23']}, {'SC': '3', 'SCGR': ['23']}],
    [{'SC': '0', 'REASON': ['08000000'], 'SCGR': ['24']}, {'SC': '1', 'REASON': ['08000000'], 'SCGR': ['24']}],
    [{'SC': '0', 'SCGR': ['20']}, {'SC': '1', 'SCGR': ['20']}],
    [{'SC': '0', 'SCGR': ['23']}, {'SC': '1', 'SCGR': ['23']}],
    [{'SC': '0', 'SCGR': ['25']}, {'SC': '1', 'SCGR': ['25']}],
    [{'SC': '0', 'SCGR': ['30']}, {'SC': '1', 'SCGR': ['30']}],
    [{'SC': '0', 'SCGR': ['40']}, {'SC': '1', 'SCGR': ['40']}],
    [{'SC': '0', 'SCGR': ['43']}, {'SC': '1', 'SCGR': ['43']}],
    [{'SC': '0', 'SCGR': ['45']}, {'SC': '1', 'SCGR': ['45']}],
    [{'SC': '0', 'SCGR': ['50']}, {'SC': '1', 'SCGR': ['50']}],
    [{'SC': '0', 'SCGR': ['60']}, {'SC': '1', 'SCGR': ['60']}, {'SC': '2', 'SCGR': ['60']}, {'SC': '3', 'SCGR': ['60']}],
    [{'SC': '0', 'SCGR': ['61']}, {'SC': '1', 'SCGR': ['61']}, {'SC': '2', 'SCGR': ['61']}, {'SC': '3', 'SCGR': ['61']}],
    [{'SC': '0', 'SCGR': ['62']}, {'SC': '1', 'SCGR': ['62']}, {'SC': '2', 'SCGR': ['62']}, {'SC': '3', 'SCGR': ['62']}],
    [{'SC': '0', 'SCGR': ['63']}, {'SC': '1', 'SCGR': ['63']}, {'SC': '2', 'SCGR': ['63']}, {'SC': '3', 'SCGR': ['63']}],
    [{'SC': '0', 'SCGR': ['64']}, {'SC': '1', 'SCGR': ['64']}, {'SC': '2', 'SCGR': ['64']}, {'SC': '3', 'SCGR': ['64']}],
    [{'SC': '0', 'SCGR': ['65']}, {'SC': '1', 'SCGR': ['65']}, {'SC': '2', 'SCGR': ['65']}, {'SC': '3', 'SCGR': ['65']}],
    [{'SC': '0', 'SCGR': ['66']}, {'SC': '1', 'SCGR': ['66']}, {'SC': '2', 'SCGR': ['66']}, {'SC': '3', 'SCGR': ['66']}],
    [{'SC': '0', 'SCGR': ['67']}, {'SC': '1', 'SCGR': ['67']}, {'SC': '2', 'SCGR': ['67']}, {'SC': '3', 'SCGR': ['67']}],
    [{'SC': '0', 'SCGR': ['68']}, {'SC': '1', 'SCGR': ['68']}, {'SC': '2', 'SCGR': ['68']}, {'SC': '3', 'SCGR': ['68']}],
    [{'SC': '0', 'SCGR': ['69']}, {'SC': '1', 'SCGR': ['69']}, {'SC': '2', 'SCGR': ['69']}, {'SC': '3', 'SCGR': ['69']}],
    [{'SC': '0', 'SCGR': ['70']}, {'SC': '1', 'SCGR': ['70']}, {'SC': '2', 'SCGR': ['70']}, {'SC': '3', 'SCGR': ['70']}],
    [{'SC': '0', 'SCGR': ['500']}],
    [{'SC': '0', 'SCGR': ['506']}, {'SC': '1', 'SCGR': ['506']}, {'SC': '2', 'SCGR': ['506']}],
    [{'SC': '0', 'SCGR': ['509']}, {'SC': '1', 'SCGR': ['509']}],
    [{'SC': '0', 'SCGR': ['510']}],
    [{'SC': '2', 'SCGR': ['510']}],
    [{'SC': '0', 'SCGR': ['510']}],
    [{'SC': '0', 'REASON': ['8'], 'SCGR': ['20']}, {'SC': '1', 'REASON': ['08000000'], 'SCGR': ['20']}],
    [{'SC': '0', 'REASON': ['FFFFFFFF'], 'SCGR': ['20']}, {'SC': '1', 'REASON': ['00000000'], 'SCGR': ['20']}],
    [{'SC': '0', 'REASON': ['FFFFFFFF'], 'SCGR': '-'}, {'SC': '1', 'REASON': ['00000000'], 'SCGR': '-'}]
]

rrbvp = """
<rrbvp:nsei=all,ncbd;
RADIO TRANSMISSION IP BSSGP VIRTUAL CONNECTION DATA

NSEI
11308

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11307

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11306

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11305

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11304

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11303

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11302

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11301

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


END 
















<rrbvp:nsei=all;
RADIO TRANSMISSION IP BSSGP VIRTUAL CONNECTION DATA

NSEI
11308

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACT IVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ACTIVE    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


NSEI
11307

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACTIVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ACTIVE    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


NSEI
11306

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACTIVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ACTIVE    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


NSEI
11305

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACTIVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ACTIVE    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


NSEI
11304

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACTIVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ACTIVE    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


NSEI
11303

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACTIVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ACTIVE    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


NSEI
11302

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACTIVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ACTIVE    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


NSEI
11301

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013

BVCI   CELL     BVCSTATE  IPDEV
  132  1131C1   ACTIVE    RTIPGPH-2
  131  1131C2   ACTIVE    RTIPGPH-1
  130  1131C3   ACTIVE    RTIPGPH-0
  129  1131C4   ACTIVE    RTIPGPH-3
  128  1132C2   ACTIVE    RTIPGPH-2
  127  1132C8   ACTIVE    RTIPGPH-1
  126  1132C9   ACTIVE    RTIPGPH-0
  125  113020A  ACTIVE    RTIPGPH-3
  124  113020B  ACTIVE    RTIPGPH-2
  123  113020C  ACTIVE    RTIPGPH-1
  122  113021A  ACTIVE    RTIPGPH-0
  121  113021B  ACTIVE    RTIPGPH-3
  120  113021C  ACTIVE    RTIPGPH-2
  119  113022A  ACTIVE    RTIPGPH-1
  118  113022B  ACTIVE    RTIPGPH-0
  117  113022C  ACTIVE    RTIPGPH-3
  116  113023A  ACTIVE    RTIPGPH-2
  115  113024A  ACTIVE    RTIPGPH-1
  114  113024B  ACTIVE    RTIPGPH-0
  113  113024C  ACTIVE    RTIPGPH-3
  112  113025A  ACTIVE    RTIPGPH-2
  111  113025B  ACTIVE    RTIPGPH-1
  110  113025C  ACTIVE    RTIPGPH-0
  109  113026A  ACTIVE    RTIPGPH-3
  108  113026B  ACTIVE    RTIPGPH-2
  107  113026C  ACTIVE    RTIPGPH-1
  106  113027A  ACTIVE    RTIPGPH-0
  105  113027B  ACTIVE    RTIPGPH-3
  104  113027C  ACTIVE    RTIPGPH-2
  103  113028A  ACTIVE    RTIPGPH-1
  102  113028B  ACTIVE    RTIPGPH-0
  101  113028C  ACTIVE    RTIPGPH-3
  100  113029A  ACTIVE    RTIPGPH-2
   99  113029B  ACTIVE    RTIPGPH-1
   98  113029C  ACTIVE    RTIPGPH-0
   97  113030A  ACTIVE    RTIPGPH-3
   96  113030B  ACTIVE    RTIPGPH-2
   95  113030C  ACTIVE    RTIPGPH-1
   94  113040A  ACTIVE    RTIPGPH-0
   93  113040B  ACTIVE    RTIPGPH-3
   92  113040C  ACTIVE    RTIPGPH-2
   91  113041A  ACTIVE    RTIPGPH-1
   90  113041B  ACTIVE    RTIPGPH-0
   89  113041C  ACTIVE    RTIPGPH-3
   88  113042A  ACTIVE    RTIPGPH-2
   87  113042B  ACTIVE    RTIPGPH-1
   86  113042C  ACTIVE    RTIPGPH-0
   85  113043A  ACTIVE    RTIPGPH-3
   84  113044A  ACTIVE    RTIPGPH-2
   83  113044B  ACTIVE    RTIPGPH-1
   82  113044C  ACTIVE    RTIPGPH-0
   81  113045A  ACTIVE    RTIPGPH-3
   80  113045B  ACTIVE    RTIPGPH-2
   79  113045C  ACTIVE    RTIPGPH-1
   78  113046A  ACTIVE    RTIPGPH-0
   77  113046B  ACTIVE    RTIPGPH-3
   76  113046C  ACTIVE    RTIPGPH-2
   75  113047A  ACTIVE    RTIPGPH-1
   74  113047B  ACTIVE    RTIPGPH-0
   73  113047C  ACTIVE    RTIPGPH-3
   72  113048A  ACTIVE    RTIPGPH-2
   71  113048B  ACTIVE    RTIPGPH-1
   70  113048C  ACTIVE    RTIPGPH-0
   69  113049A  ACTIVE    RTIPGPH-3
   68  113049B  ACTIVE    RTIPGPH-2
   67  113049C  ACTIVE    RTIPGPH-1
   66  113050A  ACTIVE    RTIPGPH-0
   65  113050B  ACTIVE    RTIPGPH-3
   64  113050C  ACTIVE    RTIPGPH-2
   63  113060A  ACTIVE    RTIPGPH-1
   62  113060B  ACTIVE    RTIPGPH-0
   61  113060C  ACTIVE    RTIPGPH-3
   60  113061A  ACTIVE    RTIPGPH-2
   59  113061B  ACTIVE    RTIPGPH-1
   58  113061C  ACTIVE    RTIPGPH-0
   57  113062A  ACTIVE    RTIPGPH-3
   56  113062B  ACTIVE    RTIPGPH-2
   55  113062C  ACTIVE    RTIPGPH-1
   54  113063A  ACTIVE    RTIPGPH-0
   53  113064A  ACTIVE    RTIPGPH-3
   52  113064B  ACTIVE    RTIPGPH-2
   51  113064C  ACTIVE    RTIPGPH-1
   50  113065A  ACTIVE    RTIPGPH-0
   49  113065B  ACTIVE    RTIPGPH-3
   48  113065C  ACTIVE    RTIPGPH-2
   47  113066A  ACTIVE    RTIPGPH-1
   46  113066B  ACTIVE    RTIPGPH-0
   45  113066C  ACTIVE    RTIPGPH-3
   44  113067A  ACTIVE    RTIPGPH-2
   43  113067B  ACTIVE    RTIPGPH-1
   42  113067C  ACTIVE    RTIPGPH-0
   41  113068A  ACTIVE    RTIPGPH-3
   40  113068B  ACTIVE    RTIPGPH-2
   39  113068C  ACTIVE    RTIPGPH-1
   38  113069A  ACTIVE    RTIPGPH-0
   37  113069B  ACTIVE    RTIPGPH-3
   36  113069C  ACTIVE    RTIPGPH-2
   35  113070A  ACTIVE    RTIPGPH-1
   34  113070B  ACTIVE    RTIPGPH-0
   33  113070C  ACTIVE    RTIPGPH-3
   32  1130160  ACTIVE    RTIPGPH-2
   31  1130161  ACTIVE    RTIPGPH-1
   30  1130162  ACTIVE    RTIPGPH-0
   29  1130163  ACTIVE    RTIPGPH-3
   28  1130164  ACTIVE    RTIPGPH-2
   27  1130165  ACTIVE    RTIPGPH-1
   26  1130166  ACTIVE    RTIPGPH-0
   25  1130167  ACTIVE    RTIPGPH-3
   24  1130168  ACTIVE    RTIPGPH-2
   23  1130169  ACTIVE    RTIPGPH-1
   22  1130170  ACTIVE    RTIPGPH-0
   21  1130171  ACTIVE    RTIPGPH-3
   20  1130172  ACTIVE    RTIPGPH-2
   19  1130173  ACTIVE    RTIPGPH-1
   18  1130174  ACTIVE    RTIPGPH-0
   17  1130175  ACTIVE    RTIPGPH-3
   16  1130176  ACTIVE    RTIPGPH-2
   15  1130177  ACTIVE    RTIPGPH-1
   14  1130178  ACTIVE    RTIPGPH-0
   13  1130179  ACTIVE    RTIPGPH-3
   12  1130180  ACTIVE    RTIPGPH-2
   11  1130181  ACTIVE    RTIPGPH-1
   10  1130182  ACTIVE    RTIPGPH-0
    9  1130183  ACTIVE    RTIPGPH-3
    8  1130184  ACTIVE    RTIPGPH-2
    7  1130185  ACTIVE    RTIPGPH-1
    6  1130186  ACTIVE    RTIPGPH-0
    5  1130187  ACTIVE    RTIPGPH-3
    4  1130188  ACTIVE    RTIPGPH-2
    3  1130189  ffffff    RTIPGPH-1
    2  1130190  ACTIVE    RTIPGPH-0


END

NSEI


SIGBVCSTATE  SGSNFEAT
ACTIVE         H'5013


NSEI
11308

SIGBVCSTATE  SGSNFEAT
ACTIVE


NSEI
11308

SIGBVCSTATE  SGSNFEAT
ACTIVE         5013


NSEI
11308

SIGBVCSTATE  SGSNFEAT
ACTIVE         H'FFFF




"""

rrbvp_param = {
    "name_key": "NSEI",
    "header": "RADIO TRANSMISSION IP BSSGP VIRTUAL CONNECTION DATA",
    "list_of_keys_to_print": [],
    "list_of_object_keys": {'SGSNFEAT': None}
}

rrbvp_expected = [
    [{'SGSNFEAT': ['5013'], 'NSEI': '11308'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11307'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11306'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11305'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11304'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11303'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11302'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11301'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11308'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11307'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11306'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11305'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11304'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11303'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11302'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11301'}],
    [],
    [{'NSEI': '11308'}],
    [{'SGSNFEAT': ['5013'], 'NSEI': '11308'}],
    [{'SGSNFEAT': ['FFFF'], 'NSEI': '11308'}]

]


class TestPrintReader(unittest.TestCase):

    def setUp(self):
        self.print_reader_rxbsp = PrintReader(rxbsp, CONFIGURATION_KEYS)
        self.print_reader_rxcap = PrintReader(rxcap, CONFIGURATION_KEYS)
        self.print_reader_rxmfp = PrintReader(rxmfp, CONFIGURATION_KEYS)
        self.print_reader_rxmsp = PrintReader(rxmsp, CONFIGURATION_KEYS)
        self.print_reader_rrscp = PrintReader(rrscp, CONFIGURATION_KEYS)
        self.print_reader_rrbvp = PrintReader(rrbvp, CONFIGURATION_KEYS)

    def _my_assert(self, my_val, expected_val, *args):
        self.assertEqual(my_val, expected_val, args[0].format(my_val, expected_val, *args[1:]))

    def test_init(self):
        subject_len_message = "Wrong number of subjects have={} expected={}, in {}"
        self._my_assert(len(self.print_reader_rxbsp.subjects), 3, subject_len_message, "rxbsp")
        self._my_assert(len(self.print_reader_rxcap.subjects), 6, subject_len_message, "rxcap")
        self._my_assert(len(self.print_reader_rxmfp.subjects), 5, subject_len_message, "rxmfp")
        self._my_assert(len(self.print_reader_rxmsp.subjects), 4, subject_len_message, "rxmsp")
        self._my_assert(len(self.print_reader_rrscp.subjects), 33, subject_len_message, "rrscp")
        self._my_assert(len(self.print_reader_rrbvp.subjects), 20, subject_len_message, "rrbvp")

    def _set_config_object(self, file_name, **kwargs):
        list_keys = []
        for key, val in kwargs["list_of_object_keys"].items():
            bits_obj = KeysObject()
            bits_obj.name = key
            bits_obj.direction = val
            list_keys += [bits_obj]
        config_object = ConfigObject()
        config_object.name_key = kwargs["name_key"]
        config_object.name_of_CANDY = file_name
        config_object.header = kwargs["header"]
        config_object.list_of_keys_to_print = kwargs["list_of_keys_to_print"]
        config_object.list_of_object_keys = list_keys
        return config_object

    def _check_values_for_object(self, print_reader, reader_param, expected):
        for subject in print_reader.subjects:
            files = {file_name for file_name in subject.file_names}
            if len(files) > 1:
                assert "To many files to choose"
            subject.file_name = subject.file_names[0]
            subject.xml_file_obj = self._set_config_object(subject.file_name, **reader_param)
        result = print_reader.get_check_values()
        for i in range(len(result)):
            self.assertEqual(result[i].parse_objects, expected[i])

    def test_get_check_values(self):
        self._check_values_for_object(self.print_reader_rxbsp, rxbsp_param, rxbsp_expected)
        self._check_values_for_object(self.print_reader_rxcap, rxcap_param, rxcap_expected)
        self._check_values_for_object(self.print_reader_rxmfp, rxmfp_param, rxmfp_expected)
        self._check_values_for_object(self.print_reader_rxmsp, rxmsp_param, rxmsp_expected)
        self._check_values_for_object(self.print_reader_rrscp, rrscp_param, rrscp_expected)
        self._check_values_for_object(self.print_reader_rrbvp, rrbvp_param, rrbvp_expected)


if __name__ == '__main__':
    unittest.main(exit=False)
