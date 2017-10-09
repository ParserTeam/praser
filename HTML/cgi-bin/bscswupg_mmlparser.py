'''
             __    __     __    __     __                             
            /\ "-./  \   /\ "-./  \   /\ \                            
            \ \ \-./\ \  \ \ \-./\ \  \ \ \____                       
             \ \_\ \ \_\  \ \_\ \ \_\  \ \_____\                      
              \/_/  \/_/   \/_/  \/_/   \/_____/                      
                                                                      
       ______   ______     ______     ______     ______     ______    
      /\  == \ /\  __ \   /\  == \   /\  ___\   /\  ___\   /\  == \   
      \ \  _-/ \ \  __ \  \ \  __<   \ \___  \  \ \  __\   \ \  __<   
       \ \_\    \ \_\ \_\  \ \_\ \_\  \/\_____\  \ \_____\  \ \_\ \_\ 
        \/_/     \/_/\/_/   \/_/ /_/   \/_____/   \/_____/   \/_/ /_/           


This module implements parser for Man-Machine Language (MML) printouts.


COMMON USAGE PRINCIPLES AND INPUT DATA (PRINTOUTS) REQUIREMENTS

1. Parsing is done by calling of parsePrintouts(printoutAsString) method of
   MMLparser class instance
   
2. Parsing process can be configured for specific printout parsing purposes
   during creation of MMLparser class instance (see its __init__ method)
   
3. Input data for printoutAsString method is string with one or many mml
   printouts to be parsed
   
4. Main printout header should be followed by empty line 

5. Header line  must be preceded with empty line

6. Header line is followed by values line

7. Non empty SINGLE lines preceded and followed by empty lines means
   start of NEW PRINTOUT SECTION, which is threaded as SEPARATE printout
   
8. Parameter name (header) should not contain spaces. In case it does,
   whole parameter name should be replaced here with its corresponding
   name in corresponding initialization (****I), change (****C) or
   set (****S) command, if possible, or spaces should be replaced with
   underlines (_).
   
9. Horizontal parameters (which names are followed by its values in the
   same line), should be specified during parser instance creation
   (in constructor) as follows:
   
   MMLparser(horizParams = ['HORIZPARAM1', 'HORIZPARAM2', ...])
    
10. Result of parsing is the list of dictionaries. Each dictionary
    represents separate object with its parameters stored as items
    of the dictionary, string with parameter name as key and parameter value
    as item value.
    Objects are distinguished by its identities. Object identity is either the
    first parameter encountered in printout or PRINTOUT SECTION, or parameter,
    present in list of object identities specified during parser instance
    creation (in constructor) as follows:
   
   MMLparser(objIds = ['OBJID1', 'OBJID2', ...])
   
   Since each parameter could have multiple values, separated by spaces, commas
   or newline character (\n)), parameter values are stored as list of strings.
   Custom delimiters for value parameters, located in one line, as well as no
   delimiters (None or '') can be specified during parser instance creation
   (in constructor) in regexp notation as follows:
   
   MMLparser(valDelimiters = 'delim1|delim2|...')
      
   If no value for the parameter present on the printout, it is not included in
   the result (except it is not subobject parameter, as dscribed below)
   
11. If parameter(s) represents identifier of some object (Subordinate
   Object identity, SubObjectId), which exists in scope of top level object
   (Parent Object), this relation should be bypassed to parser instance during
   its creation (in constructor) as follows:
   
   MMLparser(objHierarchy = {'ParentObjectName': ['SubObj1, SubObj2'...]})
   
   All parameters following first subobject identity found are treated
   as subobject related, and, therefore, stored as list of list,
   including empty values ([]), so it is possible to iterate over subobject
   identities and corresponding parameters BY THE SAME INDEX.
   In case of strict one-to-one relation between parameters it is possible
   to iterate over them by the same index without using object hierarchy model


OUTPUT DATA FORMAT DESCRIPTION

Function parsePrintouts(mmlPrintouts) is dedicated for parsing.
Result of parsing is the list of dictionaries. Each item of the list (which is dictionary)
represents one single object printed (which can be cell, RP, BLOCK, etc.).
Each item of a single dictionary (which corresponds to object) represents object parameters,
where item key is parameter name and item value is parameter value.
Key bscswupg_mmlparser.ID_PARAM_NAME (='objectIdParName') is dedicated for pointing on object
identificator parameter name.
Key bscswupg_mmlparser.COMMAND_NAME (='cmdName') points to name of the respective command
(if it was included at the beginning the printout, otherwise it will be=None).
Key bscswupg_mmlparser.SECTION_NAME (=sectName) points to name of the printout or printout section.

Multiple MML printouts are supported.

General output data representation scheme:

[
    {
    bscswupg_mmlparser.COMMAND_NAME: 'CMD1'
    bscswupg_mmlparser.ID_PARAM_NAME: idParam1,
    idParam1: ['object11Id'],
    param1: [val11, val12, ... , val1M],
    param2: [val21, val22, ... , val2N],
    subObjHeader1: [SubObj11, SubObj12, SubObj1K]
    subObjParam1: [[SO11val1, SO11val2, ...,  SO11valX], [SO12val1, SO12val2, ..., SO12valY], ..., [..., SO1KvalZ]
    ...
    paramP: [paramPVal1, paramPVal2, ... , paramPValQ]
    }
,
    {
    bscswupg_mmlparser.COMMAND_NAME: 'CMD1'
    bscswupg_mmlparser.ID_PARAM_NAME: idParam1,
    idParam1: ['object12Id'],
    ...
    }
,
# in case of new printout section (line preceded and followed by empty line)
# command and printout name is the same, but object identifier changed:
    {
    bscswupg_mmlparser.COMMAND_NAME: 'CMD1'
    bscswupg_mmlparser.ID_PARAM_NAME: idParam2,
    idParam2: ['object21Id'],
    ...
    }
,
# in case of second command's printout also provided, results of its parsing also attached to the result
# In this case, printout name, command name and object identifier (not necessary) are changed:
    {
    bscswupg_mmlparser.COMMAND_NAME: 'CMD2'
    bscswupg_mmlparser.ID_PARAM_NAME: idParamW,
    idParamW: ['objectW1'],
    ...
    },
    
    ...
# Other command's printout provided as input:    
    {
    bscswupg_mmlparser.COMMAND_NAME: 'CMDM'
    bscswupg_mmlparser.ID_PARAM_NAME: idParamM,
    idParamW: ['objectWM'],
    ...
    }
]


Created on Apr 27, 2016

@author: Dmytro Naychuk,
         Lobster team
'''

import re, collections
import textwrap

' ******************************** CONSTANTS ********************************* '

FAULT_INTERRUPTS = ['FAULT INTERRUPT',           # Parsing stops and throws ValueError exception 
                    'EOT DURING PRINTOUT']       # due to incomplete printout 

ID_PARAM_NAME    = 'objectIdParName'              # Key pointing to object identificator parameter name (header) 
COMMAND_NAME     = 'cmdName'                      # Key pointing to command name which printed current command
SECTION_NAME     = 'sectName'                     # Key pointing to printout section name (=printout header if no sections in the printout)

_DEBUG = False



def prettyPrint(results):
    '''
        Print parsing results in a pretty form
    '''
    for obj in results:
        
        for parameter in obj.keys():
            
            try:
                length = len(obj[parameter])
                print '[bscswupg_mmlparser.py] parameter', parameter, ', with length=', length
            except TypeError:
                print '[bscswupg_mmlparser.py] parameter', parameter
            
            # printing wrapped parameter value
            for printLine in textwrap.TextWrapper(width = 80).wrap(str(obj[parameter])):
                print printLine
            print
        
        print 80*'*'
        print



class MMLparser:



    def __init__(self, objIds = [], objHierarchy = {}, valDelimiters = '\s|,', horizParams = []):
        
        '''
        :param objIds: Specifies list of object identifiers to be used when parsing printout.
        This will also turns OFF changing of object identifier when new section encountered.
        
        Tip: it is useful with printouts where fake printout sections possible due to header line is printed
        but no values for its parameters and no extra empty line printed after it.


        :param objHierarchy: Specifies object hierarchy in printouts being parsed,
        as following structure of strings:
        {
        objectType1: [subObjType11, subObjType12, ..., subObjType1N],
        objectType2: [subObjType21, subObjType22, ..., subObjType2N],
        ...
        objectTypeM: [subObjTypeM1, subObjTypeM2, ..., subObjTypeMN],
        }
        
        Tip: usually, only 1 key in dictionary above should be specified. Multiple
             keys are necessary in case of parsing multiple printouts or single printout with printout sections
             which has different type of [primary] objects each with corresponding ierarchy.
             

        :param valDelimiters: Specifies delimiters used to split value of each
        parameter in a single line, in regular expression notation.
        Default value: '\s|,' (means use spaces (\s) or (|) commas (,) as value delimiter)
        
        Tip: it can be useful in case of parameter value is some text, like in RLMBP printout.
             In this case, setting valDelimiters = None or '' will cause parameter value in a single line
             will represent single item of parameter value's list. 

        :param horizParams: Specifies horizontal parameters in processed printout(s), ithat is,
        parameters, whose values are placed in the same line to the right hand. 
        '''

        if _DEBUG:
            print '[bscswupg_mmlparser.py] Call MMLparser initialization'

        # Handling kwargs
        if type(objIds) != list:
            raise ValueError('objIds should be a list (of strings with all possible object id parameters)')
        self._objIds          = objIds
        
        if type(objHierarchy) != dict:
            raise ValueError('objHierarchy should be a dictionary (with object ids as keys and list of possible sobobject ids as value)')
        self._objHierarchy = objHierarchy

        self._valDelimiters = valDelimiters

        if type(horizParams) != list:
            raise ValueError('horizParams should be a list (representing horizontal parameters)')
        self._horizParams = horizParams

        
        # ************************ INSTANCE CONSTANTS **************************
        
        # Although it is constants, it can be changed in particular parser
        # instance by direct assigning like
        # MMLparserInstance.MIN_COLUMN_SEP = 2
        # for very rare cases
        
        self.MAX_PRINTOUT_WIDTH = 72     # Parsing is done within this printout width
                                         # (according to MAXE rules)
                                                     
        self.MIN_COLUMN_SEP     = 1      # Number of spaces between columns,
                                         # 2 according to MAXE rules, but many legacy printouts require 1

        # ************************ INSTANCE VARIABLES **************************
            
        self._cmdName                   = None  # Name of command which produced currently analyzed printout
        self._sectName                  = None  # Printout or section name
        self._idParamName               = None  # Name of parameter which is object identificatior in current printout

        # Subobject model related variables
        self._curPrintoutSubObjIds      = []    # List of sobobject identificators in printout being analyzed
        self._isParamSubObjId           = False # Flag shows if current parameter is subobject identificator
        self._storeAsListOfLists        = False # Flag shows if parameter related to subobject, hence, should be stored as list of lists
        self._storeAsListOfListsParAttr = {}    # storeAsListOfLists attribute stored for each parameter
        self._isNewSubobjectStarted     = False # Flag shows whether new subobject started
        self._curSubObjId               = None  # Subobject identity stored as (name, value) for current subobject parameter
        self._curSubObjId4SubObjParam   = {}    # Stored current subobject identity values for each subobject parameter
        self._subObjCount               = {}    # Dictionary with subobject instance counters for each subobject type in current object
        self._paramParseMap             = {}    # Structure for storing parameters parse maps
        self._lineParamsBuf             = collections.OrderedDict()  # line parameters buffer dictionary      

        # Structures for storing results
        self._curObj     = collections.OrderedDict()  # Ordered dict used to keep parameters order as in printout
        self._resObjList = []



    def _cutStartEmptyLines(self, lines):
        '''
        This function cuts leading empty lines from list of lines provided.
        '''
        while lines[0] == '':
            lines.pop(0)           # Delete leading empty lines
            
        return lines



    def _cutOffPrintoutStarter(self, lines):
        
        '''
        This function cuts:
         - command line from printout and stores command name to self._cmdName, if any.
         - main printout header.
         - line with 'ORDERED' 
         - empty lines before first header line 
        '''

        lines = self._cutStartEmptyLines(lines)  # Delete leading empty lines
        
        if lines[0].rfind(';') != -1:            # If command line is first line,
            cmdNameLine = lines.pop(0)           # cut it and store later
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] cmdNameLine=', cmdNameLine
               
            # Determine command name end index, as command name can be max 7 chars
            # (according to PLEX C1 p 158)
            try:
                # either by beginning of parameter block (:)
                cmdNameLine = cmdNameLine[:cmdNameLine.index(':')]
            except ValueError:
                # or by end of command line, in case of no parameter block
                cmdNameLine = cmdNameLine[:cmdNameLine.rindex(';')]
            
            self._cmdName = cmdNameLine.upper()      # get command name from full command line
                                                     # which should be stored in a first line
            if _DEBUG:
                print '[bscswupg_mmlparser.py] _cmdName=', self._cmdName

        # Command line extracted
        lines = self._cutStartEmptyLines(lines)      # Delete leading empty lines       
        while lines[0] == 'ORDERED': lines.pop(0)    # line with ORDERED
        lines = self._cutStartEmptyLines(lines)      # Delete leading empty lines        
        
        if _DEBUG:
            print '[bscswupg_mmlparser.py] Printout lines before cutting main header:'
            for line in lines: print line

        try:
            # Cut off printout slogan as part from start till empty line
            self._sectName = lines[:lines.index('')]
        except ValueError:
            lines = []  # If no empty line, there is nothing to analyze
                    
        try:
            lines = lines[lines.index(''):]          # cut off printout header
        except ValueError:
            lines = []  # If no empty line, there is nothing to analyze

        return lines



    def _splitLine2list(self, valueLine):
        
        '''
        This function splits line to list of tokens, depending on valDelimiters parser option.
        '''

        if _DEBUG:
            print '[bscswupg_mmlparser.py] Call _splitLine2list', (valueLine)
            print '[bscswupg_mmlparser.py] self._valDelimiters=', self._valDelimiters

        if self._valDelimiters:
            # Possible multiple values in a row, separated by spaces (\s) or commas (,)
            paramValuesList = re.split(self._valDelimiters, valueLine)
             
        else:
            # Parameter values string is taken as single item of its values list
            paramValuesList = [valueLine.strip()]

        # Remove all empty strings which occurs in splitlist as a result of custom split character usage
        paramValuesList = filter(None, paramValuesList)  
        
        if _DEBUG:
            print '[bscswupg_mmlparser.py] Finish _splitLine2list()'

        return paramValuesList


        
    def _isParamLjustified(self, paramName, paramNameStartPos, paramNameEndPos, rightSearchBorder, restOfPrintoutLines):

        '''
        This internal  function checks if parameter value is left justified
        (normal case according to MAXE rules) to its header
        '''
                            
        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] call _isParamLjustified', (paramName, paramNameStartPos, paramNameEndPos, rightSearchBorder, '...')


        # Flags storing parameter L- or R -justified (default is left justified)
        
        # for current line
        isParamLjustified    = None
        isParamRjustified    = None
        
        # accumulated attributes
        areAllValsLjustified = None
        areAllValsRjustified = None
        
        
        # Combination of those initial values of isLinePossiblyParamRelated and prevLine will allow first line analysis
        isLinePossiblyParamRelated = True # Flag shows that current line related to current parameter's value
        prevLine                   = None # Stored previous line     
        
        for curLine in restOfPrintoutLines:

            if _DEBUG:
                print '[bscswupg_mmlparser.py] curLine=', curLine

            if prevLine == '':
                # If previous line is empty, current line is a header line,
                # so reevaluate if further vales lines will be related to our parameter
                # (they are if header contains parameter name we're interested in)
                
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] reevaluating isLinePossiblyParamRelated'
                    
                isLinePossiblyParamRelated = curLine[paramNameStartPos:paramNameEndPos] == paramName   

            if _DEBUG:
                print '[bscswupg_mmlparser.py] isLinePossiblyParamRelated=', isLinePossiblyParamRelated
            
            if isLinePossiblyParamRelated:

                # Check if parameter value is left justified to its header (legacy printouts) or not (modern MAXE rules)
                try:
                    isParamLjustified = curLine[paramNameStartPos] != ' '               
                    if paramNameStartPos > 0:
                        isParamLjustified = isParamLjustified and \
                                          curLine[paramNameStartPos - 1] == ' '
                                          
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] isParamLjustified=', isParamLjustified
                        
                except IndexError:
                    
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] IndexError when checking isParamLjustified, analyzing next line'
                    
                    # Means current values line is too short and therefore does not contains analyzing parameter
                    # So trying next line
                    
                    prevLine = curLine # Store previous line for next iteration
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] prevLine is changed to:', prevLine
                    
                    continue

    
                # Check if parameter value is right justified to its header (legacy printouts) or not (modern MAXE rules)
                    
                try:
                    isParamRjustified = curLine[paramNameEndPos] == ' '
                except IndexError:
                    # Means possibly right justified parameter due to right border is end of line
                    isParamRjustified = True
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] IndexError when checking isParamRjustified, assuming it is right justified to end of line'
                
                try:
                    isParamRjustified = isParamRjustified and \
                                        curLine[paramNameEndPos - 1] != ' '
                except IndexError:
                    # Means corresponding right part is unreachable due to line is too short
                    # but its ok since param value may be left justified and stored a little bit left
                    
                    # This also means that parameter can't be right justified
                    isParamRjustified = False # To avoid influence of previous iteration's result
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] IndexError when checking isParamRjustified, so it was set to False'

                if _DEBUG:
                    print '[bscswupg_mmlparser.py] isParamRjustified=', isParamRjustified
                
                    
                # Flags can be valid when they are different
                # we can trust only if left justification detected
                if isParamLjustified and not isParamRjustified:
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Different trusted justification modes detected, returning', isParamLjustified
                    return isParamLjustified

                # Evaluating accumulated attributes

                if isParamLjustified or isParamRjustified:  # do not take False, False values into consideration, as it can mean no value, so fake statistics
                    if areAllValsLjustified == None:
                        areAllValsLjustified = isParamLjustified
                    else:
                        areAllValsLjustified = areAllValsLjustified and isParamLjustified
    
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] areAllValsLjustified=', areAllValsLjustified
    
                    if areAllValsRjustified == None:
                        areAllValsRjustified = isParamRjustified
                    else:
                        areAllValsRjustified = areAllValsRjustified and isParamRjustified
    
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] areAllValsRjustified=', areAllValsRjustified

            prevLine = curLine # Store previous line for next iteration
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] prevLine is changed to:', prevLine
        
        if _DEBUG:
            print '[bscswupg_mmlparser.py] Finish _isParamLjustified(), returning final result:', areAllValsLjustified or not areAllValsRjustified

        # Final value is reverse implication (A or not B) of accumulated values, according to its truth table:
        # +-------+-------+--------+------------------------------------------------------------------------------------+
        # | All L | All R | Result | Comment                                                                            |
        # +-------+-------+--------+------------------------------------------------------------------------------------+
        # | No    | No    | Yes    | Either no values or values shifted from its header, assume default justification L |
        # | No    | Yes   | No     | For sure, R justification                                                          |
        # | Yes   | No    | Yes    | For sure, L justification                                                          |
        # | Yes   | Yes   | Yes    | All values directly under header, assume default justification L                   | 
        # +-------+-------+--------+------------------------------------------------------------------------------------+
        return areAllValsLjustified or not areAllValsRjustified



    def _finalizeObject(self):
        '''
        This function intended for storing current result object dictionary into final result list.
        '''

        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] Call _finalizeObject()'

            print '[bscswupg_mmlparser.py] before self._curObj=', self._curObj
            print '[bscswupg_mmlparser.py] before self._resObjList=', self._resObjList

        if self._curObj:
            # if any data collected,
            # store generic keys and append object to result list
            self._curObj[ID_PARAM_NAME] = self._idParamName     # store object id parameter name with fixed key
            self._curObj[COMMAND_NAME]  = self._cmdName         # store command name with fixed id key
            self._curObj[SECTION_NAME]  = self._sectName        # store printout or section name into object
            
            self._resObjList.append(self._curObj)      # append object data to result object list
            
            # Clear data
            self._curObj                = collections.OrderedDict()  # Ordered dict used to keep parameters order as in printout
            self._storeAsListOfLists    = False # reset attribute for new object
            self._curSubObjId           = None
            self._isNewSubobjectStarted = False
            self._subObjCount           = {}
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Object finalized'
                
        if _DEBUG:
            print '[bscswupg_mmlparser.py] after self._curObj=', self._curObj
            print '[bscswupg_mmlparser.py] after self._resObjList=', self._resObjList

            print '[bscswupg_mmlparser.py] _finalizeObject() finished.'


       
    def _storeParam(self, paramName, paramValues, storeAsListOfLists):
        '''
        This function stores provided parameter into current result object dictionary.
        '''
        
        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] Call _storeParam with', (paramName, paramValues, storeAsListOfLists)

        try:
            # If subobject id param value present, start new subobject
            # OR
            # if current subobject id value is empty (phantom) or the same as stored for subobject parameter,
            # it means no new subobject
            self._isNewSubobjectStarted = self._isNewSubobjectStarted                                   \
                                            or                                                          \
                                          self._curSubObjId                                             \
                                          and                                                           \
                                          self._curSubObjId[1]                                          \
                                          and                                                           \
                                          self._curSubObjId != self._curSubObjId4SubObjParam[paramName] \
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Found stored value for self._curSubObjId4SubObjParam[', paramName, ']=', self._curSubObjId4SubObjParam[paramName]
                print '[bscswupg_mmlparser.py] self._curSubObjId==', self._curSubObjId
                                     
        except KeyError:                  # Means subobject parameter is storing for first time,
            self._isNewSubobjectStarted = True  # so storing _subObjIds4SubObjParams is necessary

        if _DEBUG:
            print '[bscswupg_mmlparser.py] self._isNewSubobjectStarted=', self._isNewSubobjectStarted


        # Storing of parameter into current object                                              
        if paramName in self._curObj:             # if parameter already in current object
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Found self._curObj[',paramName,']=', self._curObj[paramName]

            if storeAsListOfLists:                    # and if this is subobject related parameter
                if self._isNewSubobjectStarted:                 # and if new subobject started (if value present in subobject id header)
                    
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Appending parameter values list to existing list of lists:'
                        print '[bscswupg_mmlparser.py] paramName==', paramName
                        print '[bscswupg_mmlparser.py] self._curObj==', self._curObj
                        print '[bscswupg_mmlparser.py] self._curSubObjId[0]==', self._curSubObjId[0]
                        print '[bscswupg_mmlparser.py] self._subObjCount==', self._subObjCount
                    
                    # if this parameter is not subobject id itself (because it causes redundand empty values for second type of subobject which treated as nested, and because redundand subobject parameter which is also subobject id is rather big fail)
                    # if this is not plain parameter duplicate of subobject parameter (like STATE in NTSTP printout; parent subobject id exists for the parameter, e.i. self._curSubObjId is not empty)
                    # and this is not phantom occurrence of subobject id parameter (subobject id is empty, but subordinate subobject parameter exists, like in RLAPP printout) 
                    if not self._isParamSubObjId and self._curSubObjId and self._curSubObjId[1]:                    
                        for i in xrange(self._subObjCount[self._curSubObjId[0]] - len(self._curObj[paramName])):
                            self._curObj[paramName].append([])          # add proper amount of empty elements
                                                                        # (used for proper matching subobject parameter values to subobject ids,
                                                                        # in case of optional subobject parameters)
                            if _DEBUG:
                                print '[bscswupg_mmlparser.py] Added empty element for subobject parameter', paramName

                    self._curObj[paramName].append(paramValues)     # add its list of values data as separate item (like list in list)
    
                    if self._curSubObjId[1]:                        # avoid phantom occurrences of the parameter (with no value)
                        self._curSubObjId4SubObjParam[paramName] = self._curSubObjId # Store current subobject id
                        if _DEBUG:
                            print '[bscswupg_mmlparser.py] Setting self._curSubObjId4SubObjParam[',paramName,']=', self._curSubObjId4SubObjParam[paramName]

                else:
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] extending last element of parameter values list:'
                        print '[bscswupg_mmlparser.py] self._curObj[',paramName,']==', self._curObj[paramName]
                        
                    self._curObj[paramName][-1].extend(paramValues) # in case it is the same subobject, extend its list-in-list

            else:                                               # if it is not subobject related parameters (plain parameters)
                if paramValues:                                 # store only in case it has some value
                    self._curObj[paramName].extend(paramValues) # if this is plain parameter, just add new values to its list of values

        else:    # Storing as new parameter

            if _DEBUG:
                print '[bscswupg_mmlparser.py] Storing new parameter into _curObj:'

            if storeAsListOfLists:                              # if this is subobject parameter
                
                self._curObj[paramName] = []
                
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] self._curSubObjId==', self._curSubObjId
                    print '[bscswupg_mmlparser.py] self._subObjCount==', self._subObjCount

                # if this parameter is not subobject id itself (because it causes redundand empty values for second type of subobject which treated as nested, and because redundand subobject parameter which is also subobject id is rather big fail)
                # if this is not plain parameter duplicate of subobject parameter (like STATE in NTSTP printout; parent subobject id exists for the parameter, e.i. self._curSubObjId is not empty)
                # and this is not phantom occurrence of subobject id parameter (subobject id is empty, but subordinate subobject parameter exists, like in RLAPP printout) 
                if not self._isParamSubObjId and self._curSubObjId and self._curSubObjId[1]:                    
                    for i in xrange(self._subObjCount[self._curSubObjId[0]]):  # add proper amount of empty elements
                        self._curObj[paramName].append([])          # (used for proper matching subobject parameter values to subobject ids,
                                                                    # in case of optional subobject parameters)
                        if _DEBUG:
                            print '[bscswupg_mmlparser.py] Added empty element for subobject parameter', paramName, 'during creation'
                
                self._curObj[paramName].append(paramValues)     # store it as list-in-list
                
                if self._isNewSubobjectStarted and self._curSubObjId[1]:  # avoid phantom occurrences of the parameter (with no value)                    
                    self._curSubObjId4SubObjParam[paramName] = self._curSubObjId  # Store current subobject id
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Setting self._curSubObjId4SubObjParam[',paramName,']=', self._curSubObjId4SubObjParam[paramName]

            else:
                if paramValues:                                 # store only in case it has some value
                    self._curObj[paramName] = paramValues       # if this is plain parameter, just store its value(s)

        if _DEBUG:
            try:
                print '[bscswupg_mmlparser.py] Finally self._curObj[', paramName, ']==', self._curObj[paramName]
            except KeyError:
                print '[bscswupg_mmlparser.py] Finally self._curObj[', paramName, '] not set due to empty value'

        # set current subobject id value for further subobject parameters        
        if self._isParamSubObjId:
            self._curSubObjId = paramName, paramValues[:]       # copy of parameter value(s) list to avoid cross modification
                                                                # by reference due to
                                                                # self._curObj[paramName] = paramValues above
                                   
            if _DEBUG:
                print '[bscswupg_mmlparser.py] self._curSubObjId=', self._curSubObjId

            self._isNewSubobjectStarted = paramValues[:]         # If subobject id param value present, start new subobject

            if _DEBUG:
                print '[bscswupg_mmlparser.py] due to _curSubObjId value self._isNewSubobjectStarted=', self._isNewSubobjectStarted
                
            if self._curSubObjId[1]:                            # avoid phantom occurrences of the parameter (with no value)
                try:
                    self._subObjCount[paramName] += 1
                except KeyError:
                    self._subObjCount[paramName] = 0

                if _DEBUG:
                    print '[bscswupg_mmlparser.py] self._subObjCount[', paramName, ']=', self._subObjCount


        if _DEBUG:
            print '[bscswupg_mmlparser.py] Finished _storeParam()'



    def _handleParam(self, paramName, paramValues):
        
        '''
        This function stores provided parameter either to line parameters buffer,
        in case of objIds parser parameter provided (needed for its proper support),
        or directly to current result object 
        '''
        
        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] Call _handleParam with', (paramName, paramValues)

        # Update object id
        # if id parameter name changed and
        # if no Object Ids specified by user and no ID parameter stored jet
        # or if parameter is listed in user specified object ids list
        if self._idParamName != paramName           \
           and                                      \
           (not (self._objIds or self._idParamName) \
               or                                   \
           paramName in self._objIds):
            
            self._finalizeObject()  # finalize current object, if any, since changing object id name means previous object completed anyway
            
            self._idParamName = paramName
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Object identity detected according to user parameter objIds, self._idParamName=', self._idParamName

            # Preparations to handle subobjects model
            try:
                self._curPrintoutSubObjIds = self._objHierarchy[self._idParamName]
            except KeyError:
                self._curPrintoutSubObjIds = []
            

        if paramName == self._idParamName and paramValues:        # Finalize object, if current parameter is non empty object id 
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] New object id encountered, finalizing object'
                print '[bscswupg_mmlparser.py] self._curObj=', self._curObj
                print '[bscswupg_mmlparser.py] paramName=', paramName
                print '[bscswupg_mmlparser.py] paramValues=', paramValues
                
            self._finalizeObject()


        # flag shows whether current parameter is subobject identificator                
        self._isParamSubObjId = paramName in self._curPrintoutSubObjIds
        if _DEBUG:
            print '[bscswupg_mmlparser.py] self._isParamSubObjId=', self._isParamSubObjId, 'for', paramName


        # handle storeAsListOfLists attribute
        try:                # if parameter attribute exists for parameter, take it
            storeAsListOfLists = self._storeAsListOfListsParAttr[paramName]

            if _DEBUG:
                print '[bscswupg_mmlparser.py] Found self._storeAsListOfListsParAttr[', paramName, ']=', self._storeAsListOfListsParAttr[paramName]
                 
        except KeyError:    # otherwise continue with current object based value (self._storeAsListOfLists)
            storeAsListOfLists = self._storeAsListOfListsParAttr[paramName] = self._storeAsListOfLists
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Not found self._storeAsListOfListsParAttr[', paramName, '], using self._storeAsListOfLists=', self._storeAsListOfLists


        # Store parameter either to current object or line buffer
        if self._objIds:            
            # custom object id may be not first in line,
            # so storing to line parameter buffer is needed to detect
            # and handle such situation properly
            self._lineParamsBuf[paramName] = (paramValues, storeAsListOfLists)

            if _DEBUG:
                print '[bscswupg_mmlparser.py] Added parameter', paramName, 'to self._lineParamsBuf'
                print '[bscswupg_mmlparser.py] self._lineParamsBuf=', self._lineParamsBuf 

        else:
            # if custom object ids not specified, than default behavior
            # Store result to return
            self._storeParam(paramName,
                             paramValues,
                             storeAsListOfLists)

        # set flag once for next parameters in current object
        # if subheader was met
        if not self._storeAsListOfLists:
            self._storeAsListOfLists = self._isParamSubObjId
            if _DEBUG:
                print '[bscswupg_mmlparser.py] _storeAsListOfLists=', self._storeAsListOfLists

        if _DEBUG:
            print '[bscswupg_mmlparser.py] Finished _handleParam()'

                
        
    def _storeLineParams(self):
        '''
        This function stores parameters collected per line (in case of objIds parser parameter specified), if any
        '''
        
        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] call _storeLineParams()'

        
        for paramName, (paramValues, storeAsListOfLists) in self._lineParamsBuf.iteritems():
            
            # flag shows whether current parameter is subobject identificator                
            self._isParamSubObjId = paramName in self._curPrintoutSubObjIds
            if _DEBUG:
                print '[bscswupg_mmlparser.py] self._isParamSubObjId=', self._isParamSubObjId, 'for', paramName

            self._storeParam(paramName,
                             paramValues,
                             storeAsListOfLists)
            
        self._lineParamsBuf = collections.OrderedDict()  # Clearing parameter line buffer

        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] Finish _storeLineParams()'
        


    def _parseParamLine(self, headerLine, valueLine, restOfPrintoutLines):
        
        '''
        This function parses line with parameter valueLine basing on line with parameter headerLine
        and returns parameters mapped to its values as dictionary.
        '''
    
        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] call _parseParamLine', (headerLine, valueLine, '...')
    
                
        paramNames                   = []    # List of parameter headers in current headerline
        
        # Parameter's justification 
        isCurParamLJustified         = None
        isRightParamLJustified       = None
        
        paramValues                  = []    # List with current parameter values
       
        try:
            # If such header line found it means it was already parsed,
            # so reusing its right-parse map (parameter name, start index)

            for paramName, curParamValSearchStartPos, curParamValSearchEndPos in self._paramParseMap[headerLine]:

                if _DEBUG:
                    print '[bscswupg_mmlparser.py] Analyzing parameter', paramName, 'by stored map:', (curParamValSearchStartPos, curParamValSearchEndPos)
                 
                paramValues = self._splitLine2list(valueLine[curParamValSearchStartPos:curParamValSearchEndPos])
                                
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] paramValues=', paramValues
                
                self._handleParam(paramName, paramValues)
        
        except KeyError:
            
            # If such header line not found it means it should be parsed from scratch
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Parsing such headerLine for first time:'
                print headerLine

            # Initially to start search from 0 position, because of adding MIN_COLUMN_SEP below
            leftParamNameEndPos = -self.MIN_COLUMN_SEP
            leftParamValSearchEndPos  = 0  # Unlike parameter names, parameter values not necessary must be separated by self.MIN_COLUMN_SEP, so no adding 1, so initial value is 0

            # Lists to store data for building parameters parse map 
            paramValSearchStartPositions       = []
            paramValSearchEndPositions         = []

            # Split headerline by 1 space, not by MIN_COLUMN_SEP amount of them
            # since some printouts violate corresponding MAXE rule (like RLLLP's one) 
            paramNames = headerLine.split()

            if _DEBUG:
                print '[bscswupg_mmlparser.py] paramNames=', paramNames
            
            for i in xrange(len(paramNames)):       # Iterating over parameter names
                                                    # from lefto to the right

                # Get parameter name
                paramName = paramNames[i]                
            
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] analyzing for first time parameter paramName=', paramName
                
                # Get start and end (non inclusive!) positions for parameter name (header)
                
                # Search with Start and End positions to avoid collisions during search and for speed up
                curParamNameStartPos = headerLine.index(paramName,
                                                        leftParamNameEndPos + self.MIN_COLUMN_SEP,
                                                        self.MAX_PRINTOUT_WIDTH + 1) # +1 due to End search position not included
                
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] curParamNameStartPos=', curParamNameStartPos
                
                curParamNameEndPos = curParamNameStartPos + len(paramName) # Calculate position of header's last character
                
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] curParamNameEndPos=', curParamNameEndPos


                # **************************************************************
                # *          CALCULATING curParamValSearchStartPos                   *
                # **************************************************************

                # start = leftParam searchEnd + MIN_COLUMN_SEP
                curParamValSearchStartPos = leftParamValSearchEndPos

                if _DEBUG:
                    print '[bscswupg_mmlparser.py] curParamValSearchStartPos = ', curParamValSearchStartPos

                # **************************************************************
                # *            CALCULATING curParamValSearchEndPos                   *
                # **************************************************************
                
                # Get characteristics from right parameter, which are necessary below
                try:
                    rightParamName = paramNames[i + 1]
                    rightParamNameStartPos = headerLine.index(rightParamName,
                                                         curParamNameEndPos + self.MIN_COLUMN_SEP,
                                                         self.MAX_PRINTOUT_WIDTH + 1)
                    rightParamNameEndPos = rightParamNameStartPos + len(rightParamName)
                    
                except IndexError:
                    rightParamName = None
                    rightParamNameStartPos = self.MAX_PRINTOUT_WIDTH + 1
                
                
                # Check if parameter value is right justified to its header
                if isRightParamLJustified == None:       # if value is not valid
                    # Calculate property, if not previously stored
                    isCurParamLJustified = self._isParamLjustified(paramName,
                                                                   curParamNameStartPos,
                                                                   curParamNameEndPos,
                                                                   rightParamNameStartPos,
                                                                   restOfPrintoutLines)
                else:
                    # Reuse property collected on previous iteration
                    isCurParamLJustified = isRightParamLJustified
                
                
                if isCurParamLJustified:
                    
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Parameter', paramName, 'is left justified'
                    
                    # to find End values position, check of next parameter adjustment required
                    if rightParamName:
                        
                        if _DEBUG:
                            print '[bscswupg_mmlparser.py] rightParamName=', rightParamName
                            
                        # Detecting characteristics of next one to the right hand from current parameter
                        # for _isParamLjustified method 
                        try:
                            rightRightParamNameStartPos = headerLine.index(paramNames[i + 2], # rightRightParamName
                                                                          rightParamNameEndPos + self.MIN_COLUMN_SEP,
                                                                        self.MAX_PRINTOUT_WIDTH + 1)
                            
                        except IndexError:
                            rightRightParamNameStartPos = self.MAX_PRINTOUT_WIDTH + 1

                        isRightParamLJustified = self._isParamLjustified(rightParamName,
                                                                         rightParamNameStartPos,
                                                                         rightParamNameEndPos,
                                                                         rightRightParamNameStartPos,
                                                                         restOfPrintoutLines)

                        if _DEBUG:
                            print '[bscswupg_mmlparser.py] isRightParamLJustified=', isRightParamLJustified
                        
                        if isRightParamLJustified:
                            
                            # in case next parameter (to the right hand from current) is also left justified,
                            # take curParamValSearchEndPos as rightParamNameStartPos since parameter value may be closely (without spaces) to right side parameter    
                            curParamValSearchEndPos = rightParamNameStartPos
 
                            if _DEBUG:
                                print '[bscswupg_mmlparser.py] Right parameter is left justified, curParamValSearchEndPos=', curParamValSearchEndPos
                        else:
                            
                            # When adjustment is changed, it is most tricky case (for instance, see SASTP's printout),
                            # as we cannot be sure where exactly current parameter values end and where next parameter's values begin.
                            # So rest of the lines in printout which contains corresponding parameters values, should be examined
                            # and top right position for current parameter detected.
                        
                            if _DEBUG:
                                print '[bscswupg_mmlparser.py] Adjustment changed, start of searching curParamValMaxEndPos'
                                                        
                            curParamValMaxEndPos = None # Initially None                                                         
                            isLinePossiblyParamRelated = True # Flag shows that current line contains current parameter's value                              
                            prevLine             = None # Stored previous line

                            for curLine in restOfPrintoutLines:
                                
                                if prevLine != '':  # value lines should not be preceded with empty line
                                      
                                    # take into consideration only lines containing values related to corresponding header line
                                    # and only in case both current parameter and right parameter present (if line end reaches right parameter column)
                                    if isLinePossiblyParamRelated and \
                                       len(curLine) >= rightParamNameStartPos:
                                        
                                        if _DEBUG:
                                            print '[bscswupg_mmlparser.py] curLine=', curLine
                                        
                                        try:
                                            # get border of parameter values as rindex of column separator occurrence between current and right parameter headers
                                            # rindex instead of index() used due to some values even can be separated by more than 2 spaces (which is column separator), like in EXRUP printout
                                            curParamValSearchEndPos = curLine.rindex(' ' * self.MIN_COLUMN_SEP,
                                                                               curParamNameStartPos,
                                                                               rightParamNameStartPos)
                                            if _DEBUG:
                                                print '[bscswupg_mmlparser.py] curParamValSearchEndPos=', curParamValSearchEndPos
                                                
                                            if not curParamValMaxEndPos:
                                                # only for first iteration
                                                curParamValMaxEndPos = curParamValSearchEndPos
                                            
                                            # minimum value is taken since in case detected FIRST right space is closer to left
                                            # it means that right hand parameter starts more to the left side
                                            curParamValMaxEndPos = min(curParamValSearchEndPos, curParamValMaxEndPos)
                                            
                                            if _DEBUG:
                                                print '[bscswupg_mmlparser.py] curParamValMaxEndPos=', curParamValMaxEndPos
                                            
                                        except ValueError:
                                            
                                            if _DEBUG:
                                                print '[bscswupg_mmlparser.py] This line does not contains data in columns we are interested in'
                                            # Means this line does not contains data in columns we are interested in
                                            # so proceed with next line(s)
                                            pass

                                else:
                                    # If previous line is empty, current line is a header line,
                                    # so reevaluate if further vales lines will be related to our parameter
                                    # (they are if header contains parameter name we're interested in, in the right place, of course)
                                    isLinePossiblyParamRelated = curLine[curParamNameStartPos:curParamNameEndPos] == paramName  
                                
                                prevLine = curLine # Store previous line for next iteration
                            
                            # end = max right margin
                            curParamValSearchEndPos = curParamValMaxEndPos
                            
                            if _DEBUG:
                                print '[bscswupg_mmlparser.py] Search due to changed justification found curParamValSearchEndPos=', curParamValSearchEndPos
                    else:
                        
                        # Means no next parameter (to the right hand from current)
                        if _DEBUG:
                            print '[bscswupg_mmlparser.py] no next parameter (to the right hand from current)'

                        curParamValSearchEndPos = self.MAX_PRINTOUT_WIDTH + 1  # +1 due to End search position not included
                        
                        if _DEBUG:
                            print '[bscswupg_mmlparser.py] curParamValSearchEndPos = ', curParamValSearchEndPos

                else:            # Parameter is Right-justified
                    
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Parameter', paramName, 'is right justified'
                    
                    # end = curParamNameEndPos
                    curParamValSearchEndPos = curParamNameEndPos

                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] curParamValSearchEndPos = ', curParamValSearchEndPos
                    
                    isRightParamLJustified = None # marking value as not valid, so it will be recalculated
                                                  # during next iterations, if needed
                    
                # **************************************************************
                # *          END OF CALCULATING curParamValSearchEndPos              *
                # **************************************************************

                
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] Cutting values from,', curParamValSearchStartPos, 'till', curParamValSearchEndPos

                paramValues = self._splitLine2list(valueLine[curParamValSearchStartPos:curParamValSearchEndPos])

                if _DEBUG:
                    print '[bscswupg_mmlparser.py] paramValues=', paramValues


                self._handleParam(paramName, paramValues)
                
                # Build lists to store as parse map
                paramValSearchStartPositions.append(curParamValSearchStartPos)
                paramValSearchEndPositions.append(curParamValSearchEndPos)
                
                # Store relevant data for next iteration                 
                leftParamNameEndPos  = curParamNameEndPos
                leftParamValSearchEndPos   = curParamValSearchEndPos

            # store parse parameters for current header line
            self._paramParseMap[headerLine] = zip(paramNames, paramValSearchStartPositions, paramValSearchEndPositions)

        # Store parameters in line buffer, if any
        self._storeLineParams()



    def _hasLineHorizParams(self, line):
        '''
        This function checks if provided line has horizontal parameters
        '''
        for horizParam in self._horizParams:
            if horizParam in line:
                return True
        
        return False



    def _parseHorizontalLine(self, line):
        
        '''
        This function parses horizontal parameters, which are defined by user
        as parser parameter horizParams (see MMLparser constructor).
        and are in the same line as values, e.g.
        
        PARAM1: VAL11,VAL12 VAL13 PARAM2: VAL21
        '''
        
        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] Call _parseHorisontal with', (line)
            print '[bscswupg_mmlparser.py] self._curObj=', self._curObj
            print '[bscswupg_mmlparser.py] self._horizParams=', self._horizParams
        
        # Initially just split by spaces
        tokens = self._splitLine2list(line)
                                                        
        if _DEBUG:
            print '[bscswupg_mmlparser.py] tokens=', tokens

        paramName = None
        paramValues = []
        result = {}
         
        for token in tokens:
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Processing token', token

            if token in self._horizParams:           # If new parameter name encountered
                
                # store existing parameter and its values
                self._handleParam(paramName, paramValues)
                    
                paramName = token
                paramValues = []
            else:
                paramValues.extend(self._splitLine2list(token))

        # store last parameter, as it cannot be handled in a loop above
        self._handleParam(paramName, paramValues)
        
        # Store parameters in line buffer, if any
        self._storeLineParams()

        if _DEBUG:
            print '[bscswupg_mmlparser.py] Finished _parseHorisontal()'
            print '[bscswupg_mmlparser.py] self._curObj=', self._curObj
      
        

    def _handlePrintoutLines(self, printoutLines):
        '''
        This function iterates over printout lines (result of splitlines())
        and handle each of them.
        '''
        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] _handlePrintoutLines started for command', self._cmdName
            print '[bscswupg_mmlparser.py] printoutLines:'
            print printoutLines
             
        try:
            curPrintoutEndIx = printoutLines.index('END')
        except ValueError:
            curPrintoutEndIx = None

        if _DEBUG:
            print '[bscswupg_mmlparser.py] curPrintoutEndIx=', curPrintoutEndIx
        
        curHeaderLine = None                     # Header line current parameter line(s) are related to
        
        prevLine = ''
        nextLine = ''

        
        for i in xrange(len(printoutLines)):            
            line = printoutLines[i]
            
            if _DEBUG:
                print '[bscswupg_mmlparser.py] Handling line:'
                print line
                print '[bscswupg_mmlparser.py] i=', i
            
            if i > 0:
                prevLine = printoutLines[i - 1]

            if i < len(printoutLines) - 1:
                nextLine = printoutLines[i + 1]
            else:
                nextLine = ''
   
            if i < len(printoutLines) - 2:
                nextNextLine = printoutLines[i + 2]
            else:
                nextNextLine = ''


            if line == 'END':                    # End of printout or section reached

                if _DEBUG:
                    print '[bscswupg_mmlparser.py] Line with END or NONE reached'
                
                self._finalizeObject()
                
                if _DEBUG:
                    print '[bscswupg_mmlparser.py] Handling of rest printouts, if any, started'

                try:
                    # add result of rest printout parsing to result object list
                    # parsePrintouts method used since further part may contain full printouts

                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Rest printouts:'
                        print printoutLines[i + 1:]
                    
                    self._resObjList.extend(MMLparser(objIds        = self._objIds,
                                                      objHierarchy  = self._objHierarchy,
                                                      valDelimiters = self._valDelimiters,
                                                      horizParams   = self._horizParams).parsePrintouts(printoutLines[i + 1:]))
                    
                except IndexError:
                    # Means no more lines found
                    pass

                if _DEBUG:
                    print '[bscswupg_mmlparser.py] Current printout handling finished'
            
                break                            # Break a loop and return result

            elif line in FAULT_INTERRUPTS:       # Printout interrupted,
                raise ValueError                 # consider as error
                    
            elif line != '' or prevLine == curHeaderLine: # do not handle empty line if previous line is not current headerline
                                                          # since empty line should only be handled in case it is value line,
                                                          # means previous line should be current header line
                if self._hasLineHorizParams(line):
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Horizontal parameters found'
                        
                    self._parseHorizontalLine(line)
                
                elif prevLine == '':               # If previous line is empty                          

                    if nextLine == '' and nextNextLine != '':
                        # if next line (but not next after next, otherwise it is
                        # header line with empty values next to it) is empty as well,
                        # it is threaded as new printout section,
                        # which in turn is handled as new printout

                        if _DEBUG:
                            print '[bscswupg_mmlparser.py] Printout section found:', line

                        if not self._objIds:        # if id parameter name not specified by user,
                            self._finalizeObject()      # Store current object
                            self._idParamName = None    # prepare for storing new Object ID in new section

                        # Store section name for following objects
                        self._sectName = line

                    else:                        
                        curHeaderLine = line     # it means current line is header line
                    
                else:       # Otherwise current line is parameter values line

                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] Handling parameter values'
                         
                    self._parseParamLine(curHeaderLine, line, printoutLines[i:curPrintoutEndIx])
                    
                    if _DEBUG:
                        print '[bscswupg_mmlparser.py] _parseParamLine finished'
                        
                                
            if _DEBUG:
                print '[bscswupg_mmlparser.py] ****** PRINTOUT LINE HANDLING SUMMARY ******'
                print '[bscswupg_mmlparser.py] prevLine=', prevLine
                print '[bscswupg_mmlparser.py] line    =', line
                print '[bscswupg_mmlparser.py] nextLine=', nextLine
                print '[bscswupg_mmlparser.py] curHeaderLine=', curHeaderLine
                print '[bscswupg_mmlparser.py] self._curObj=', self._curObj
                print '[bscswupg_mmlparser.py] self._resObjList=', self._resObjList

        self._finalizeObject() # May be necessary in case no END present in the printout

        if _DEBUG:
            print '[bscswupg_mmlparser.py] Finished iterating over printout lines'



    def parsePrintouts(self, printouts):
        
        '''
        This is worker function. It takes printout as string or list of lines
        due to its recursive nature (for parsing multiple printouts).
        '''
        
        self._idParamName = None

        if _DEBUG:
            print
            print '[bscswupg_mmlparser.py] Start handling of NEW printout, call parsePrintouts()'
            
        if type(printouts) == str:
            # convert printout to list of lines if sting provided
            printouts = printouts.splitlines()
        elif type(printouts) != list:
            raise ValueError # either string or list argument type expected 

            
        # Cut off command line and main header
        printouts = self._cutOffPrintoutStarter(printouts)
        
        if _DEBUG:
            print '[bscswupg_mmlparser.py] lines without printout header:', printouts 
    
        self._handlePrintoutLines(printouts)

        # Filter printout with no data represented as NONE object, return empty list instead 
        try:
            if len(self._resObjList) == 1 and \
               self._resObjList[0][self._idParamName] == ['NONE']:
                self._resObjList = []
        except KeyError:
            # If no value for object id (like it can be in EXPOP printout with data present but not for ObjectId EMG)
            pass # than it is not a NONE case for sure, so do nothing
        
        return self._resObjList



# Following part is related to module testing
if __name__ == '__main__':
       
    rlsvpALL = '''
RLSVP:CELL=ALL,PSVTYPE=BCCHPS;
CELL POWER SAVINGS DATA

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
174320A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
174330A  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
310A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
309A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
308A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
307A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
306A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
305A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
304A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
303A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
302A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
301A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
300A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
112C202  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
111C201  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
102C194  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
101C193  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
092C186  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
091C185  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
082C179  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
082C178  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
081C177  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
072C171  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
072C170  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
071C169  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
042C144  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
042C143  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
042C142  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
041C141  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
032C134  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
032C133  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
032C132  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
031C131  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
022C124  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
022C123  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
021C122  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
021C121  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
012C114  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
012C113  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
011C112  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
011C111  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
170C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
170B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
170A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
169C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
169B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
169A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
168C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
168B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
168A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
167C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
167B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
167A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
166C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
166B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
166A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
165C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
165B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
165A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
164C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
164B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
164A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
163A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
162C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
162B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
162A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
161C     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
161B     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
161A     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
160C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
160B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
160A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
150C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
150B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
150A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
149C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
149B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
149A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
148C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
148B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
148A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
147C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
147B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
147A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
146C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
146B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
146A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
145C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
145B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
145A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
144C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
144B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
144A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
143A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
142C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
142B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
142A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
141C     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
141B     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
141A     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
140C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
140B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
140A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
130C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
130B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
130A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
129C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
129B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
129A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
128C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
128B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
128A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
127C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
127B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
127A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
126C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
126B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
126A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
125C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
125B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
125A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
124C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
124B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
124A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
123A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
122C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
122B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
122A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
121C     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
121B     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
121A     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
120C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
120B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
120A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
110C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
110B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
110A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
109C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
109B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
109A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
108C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
108B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
108A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
107C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
107B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
107A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
106C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
106B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
106A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
105C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
105B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
105A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
104C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
104B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
104A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
103A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
102C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
102B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
102A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
101C     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
101B     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
101A     ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
100C     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
100B     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
100A     INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
90C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
90B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
90A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
89C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
89B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
89A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
88C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
88B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
88A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
87C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
87B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
87A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
86C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
86B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
86A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
85C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
85B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
85A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
84C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
84B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
84A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
83A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
82C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
82B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
82A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
81C      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
81B      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
81A      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
80C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
80B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
80A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
70C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
70B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
70A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
69C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
69B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
69A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
68C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
68B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
68A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
67C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
67B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
67A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
66C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
66B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
66A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
65C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
65B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
65A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
64C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
64B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
64A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
63A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
62C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
62B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
62A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
61C      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
61B      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
61A      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
60C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
60B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
60A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
50C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
50B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
50A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
49C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
49B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
49A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
48C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
48B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
48A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
47C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
47B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
47A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
46C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
46B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
46A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
45C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
45B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
45A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
44C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
44B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
44A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
43A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
42C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
42B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
42A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
41C      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
41B      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
41A      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
40C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
40B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
40A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
30C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
30B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
30A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
29C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
29B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
29A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
28C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
28B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
28A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
27C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
27B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
27A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
26C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
26B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
26A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
25C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
25B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
25A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
24C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
24B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
24A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
23A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
22C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
22B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
22A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
21C      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
21B      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
21A      ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
20C      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
20B      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
20A      INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1362C7   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1362C6   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1362C5   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1362C4   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1362C3   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1362C2   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1362C1   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1361C7   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1361C6   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1361C5   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1361C4   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1361C3   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1361C2   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1361C1   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

END

'''
    
    rrsspAll = '''
rrssp:scgr=all;
RADIO TRANSMISSION SUPER CHANNEL GROUP USE STATUS

SCGR  RP    SC  CSCH  PSCH  TEI
  20    48  0     0     0   62
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  23    48  0     0     0   62
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  25    48  0     0     0   62
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  30    48  0     0     0   62
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  40    48  0     0     0   62
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  43    48  0     0     0   62
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  45    48  0     0     0   62
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  50    48  0     0     0   
            1     0     0   62

SCGR  RP    SC  CSCH  PSCH  TEI
  60    48  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  61    46  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  62    39  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  63    44  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  64    48  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  65    37  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  66    44  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  67    39  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  68    46  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  69    37  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
  70    48  0     0     0   62
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1811    48  0     0     0   
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1813    46  0     0     0   
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1823    39  0     0     0   
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1831    48  0     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1832    37  0     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1833    48  0     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1842    48  0     0     1    0   1
            1     0     0    2   3
                            62

SCGR  RP    SC  CSCH  PSCH  TEI
1871    44  0     0     0   
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1872    44  0     0     0   
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1873    37  0     0     0   
            1     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1881    48  0     0     0   
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1882    39  0     0     0   
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1894    46  0     0     0   
            1     0     0   
            2     0     0   
            3     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1911    37  0     0     0   

SCGR  RP    SC  CSCH  PSCH  TEI
1912    44  0     0     0   

END

'''

    exrupAll = '''
EXRUP:RP=ALL;
RP SOFTWARE UNIT DATA


RP    TYPE     TWIN
   0  RPSCB1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPMMR         9000/CXC 146 20        R2B01         86  30
RPMBHR        9000/CXC 146 21        R6A06        104  29
RPIFDR        9000/CXC 146 23        R1A01         66  28
INETR         9000/CXC 146 151       R1C01         80  27
SCBSNMPR      9000/CXC 146 143       R3A04         67  26
SCBSWMGR      9000/CXC 146 145       R2F01        268  25
RIEXR         9000/CXC 146 097       R6G01        267  16


RP    TYPE     TWIN
   1  RPSCB1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPMMR         9000/CXC 146 20        R2B01         86  30
RPMBHR        9000/CXC 146 21        R6A06        104  29
RPIFDR        9000/CXC 146 23        R1A01         66  28
INETR         9000/CXC 146 151       R1C01         80  27
SCBSNMPR      9000/CXC 146 143       R3A04         67  26
SCBSWMGR      9000/CXC 146 145       R2F01        268  25
RIEXR         9000/CXC 146 097       R6G01        267  16


RP    TYPE     TWIN
  32  RPSCB1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPMMR         9000/CXC 146 20        R2B01         86  30
RPMBHR        9000/CXC 146 21        R6A06        104  29
RPIFDR        9000/CXC 146 23        R1A01         66  28
INETR         9000/CXC 146 151       R1C01         80  27
RIEXR         9000/CXC 146 097       R6G01        267  16


RP    TYPE     TWIN
  33  RPSCB1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPMMR         9000/CXC 146 20        R2B01         86  30
RPMBHR        9000/CXC 146 21        R6A06        104  29
RPIFDR        9000/CXC 146 23        R1A01         66  28
INETR         9000/CXC 146 151       R1C01         80  27
RIEXR         9000/CXC 146 097       R6G01        267  16


RP    TYPE     TWIN
  34  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
XMR           9000/CXC 146 31        R3B01        126   0   0


RP    TYPE     TWIN
  35  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
XMR           9000/CXC 146 31        R3B01        126   0   0


RP    TYPE     TWIN
  37  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPPGWR      7/CXC 146 1652/4000    R1A01        329   8   8
RTPGWFWR      7/CXC 146 1743/5000    R1A01        151   2   2
RTPGCSR       7/CXC 146 1741/5000    R1A01        144   1   1
RTPGSR        7/CXC 146 1740/5000    R1A01        123   0   0


RP    TYPE     TWIN
  39  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPPGWR      7/CXC 146 1652/4000    R1A01        329   8   8
RTPGWFWR      7/CXC 146 1743/5000    R1A01        151   2   2
RTPGCSR       7/CXC 146 1741/5000    R1A01        144   1   1
RTPGSR        7/CXC 146 1740/5000    R1A01        123   0   0


RP    TYPE     TWIN
  40  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  41  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  42  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  43  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  44  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPPGWR      7/CXC 146 1652/4000    R1A01        329   8   8
RTPGWFWR      7/CXC 146 1743/5000    R1A01        151   2   2
RTPGCSR       7/CXC 146 1741/5000    R1A01        144   1   1
RTPGSR        7/CXC 146 1740/5000    R1A01        123   0   0


RP    TYPE     TWIN
  46  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPPGWR      7/CXC 146 1652/4000    R1A01        329   8   8
RTPGWFWR      7/CXC 146 1743/5000    R1A01        151   2   2
RTPGCSR       7/CXC 146 1741/5000    R1A01        144   1   1
RTPGSR        7/CXC 146 1740/5000    R1A01        123   0   0


RP    TYPE     TWIN
  48  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPPGWR      7/CXC 146 1652/4000    R1A01        329   8   8
RTPGWFWR      7/CXC 146 1743/5000    R1A01        151   2   2
RTPGCSR       7/CXC 146 1741/5000    R1A01        144   1   1
RTPGSR        7/CXC 146 1740/5000    R1A01        123   0   0


RP    TYPE     TWIN
  50  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
ETM2R         9000/CXC 146 165       R1F01         20   0   0


RP    TYPE     TWIN
  51  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
ETM2R         9000/CXC 146 165       R1F01         20   0   0


RP    TYPE     TWIN
  54  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
CLMR          9000/CXC 146 30        R1S01        114   0   0


RP    TYPE     TWIN
  64  RPSCB1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPMMR         9000/CXC 146 20        R2B01         86  30
RPMBHR        9000/CXC 146 21        R6A06        104  29
RPIFDR        9000/CXC 146 23        R1A01         66  28
INETR         9000/CXC 146 151       R1C01         80  27
RIEXR         9000/CXC 146 097       R6G01        267  16


RP    TYPE     TWIN
  65  RPSCB1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPMMR         9000/CXC 146 20        R2B01         86  30
RPMBHR        9000/CXC 146 21        R6A06        104  29
RPIFDR        9000/CXC 146 23        R1A01         66  28
INETR         9000/CXC 146 151       R1C01         80  27
RIEXR         9000/CXC 146 097       R6G01        267  16


RP    TYPE     TWIN
  66  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
XMR           9000/CXC 146 31        R3B01        126   0   0


RP    TYPE     TWIN
  67  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
XMR           9000/CXC 146 31        R3B01        126   0   0


RP    TYPE     TWIN
  69  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPIFDR        9000/CXC 146 03        R1A08          8  31
RPFDR         9000/CXC 146 05        R1A03         10  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTAGWFWR      7/CXC 146 1771/5000    R1A01        118  15  15
RTIPAGWR      7/CXC 146 1659/4000    R1A01        321   8   8
RTAGWSR       7/CXC 146 1769/5000    R1A01        142   1   1
RTAGWR        7/CXC 146 1768/5000    R1A01        119   0   0


RP    TYPE     TWIN
  71  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPIFDR        9000/CXC 146 03        R1A08          8  31
RPFDR         9000/CXC 146 05        R1A03         10  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTAGWFWR      7/CXC 146 1771/5000    R1A01        118  15  15
RTIPAGWR      7/CXC 146 1659/4000    R1A01        321   8   8
RTAGWSR       7/CXC 146 1769/5000    R1A01        142   1   1
RTAGWR        7/CXC 146 1768/5000    R1A01        119   0   0


RP    TYPE     TWIN
  72  GARP1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 125       R4G01         81  29
GPEXR         9000/CXC 146 092       R8L01        106  16
SCTPR         9000/CXC 146 202       R6C02        339   1   1
IPR           9000/CXC 146 087       R3B02         85   0   0


RP    TYPE     TWIN
  73  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPIFDR        9000/CXC 146 03        R1A08          8  31
RPFDR         9000/CXC 146 05        R1A03         10  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPTRHR      7/CXC 146 1696/4000    R1A01        330   8   8
RCSCB2R       7/CXC 146 1690/4000    R1A02        101   7   7
RCLCCHR       7/CXC 146 1759/5000    R1A02        147   6   6
RQRCQSR       7/CXC 146 1763/5000    R1A02        153   5   5
RQUNCR        7/CXC 146 1693/4000    R1A01        307   4   4
RCSCBR        7/CXC 146 1689/4000    R1A04        107   3   3
RMPAGR        7/CXC 146 1765/5000    R1A03        157   2   2
RHTRHR        7/CXC 146 1766/5000    R1A01        132   1   1
RHLAPDR       7/CXC 146 1691/4000    R1A04        283   0   0


RP    TYPE     TWIN
  74  GARP1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 125       R4G01         81  29
GPEXR         9000/CXC 146 092       R8L01        106  16
SCTPR         9000/CXC 146 202       R6C02        339   1   1
IPR           9000/CXC 146 087       R3B02         85   0   0


RP    TYPE     TWIN
  75  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPIFDR        9000/CXC 146 03        R1A08          8  31
RPFDR         9000/CXC 146 05        R1A03         10  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPTRHR      7/CXC 146 1696/4000    R1A01        330   8   8
RCSCB2R       7/CXC 146 1690/4000    R1A02        101   7   7
RCLCCHR       7/CXC 146 1759/5000    R1A02        147   6   6
RQRCQSR       7/CXC 146 1763/5000    R1A02        153   5   5
RQUNCR        7/CXC 146 1693/4000    R1A01        307   4   4
RCSCBR        7/CXC 146 1689/4000    R1A04        107   3   3
RMPAGR        7/CXC 146 1765/5000    R1A03        157   2   2
RHTRHR        7/CXC 146 1766/5000    R1A01        132   1   1
RHLAPDR       7/CXC 146 1691/4000    R1A04        283   0   0


RP    TYPE     TWIN
  76  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  77  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPIFDR        9000/CXC 146 03        R1A08          8  31
RPFDR         9000/CXC 146 05        R1A03         10  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPTRHR      7/CXC 146 1696/4000    R1A01        330   8   8
RCSCB2R       7/CXC 146 1690/4000    R1A02        101   7   7
RCLCCHR       7/CXC 146 1759/5000    R1A02        147   6   6
RQRCQSR       7/CXC 146 1763/5000    R1A02        153   5   5
RQUNCR        7/CXC 146 1693/4000    R1A01        307   4   4
RCSCBR        7/CXC 146 1689/4000    R1A04        107   3   3
RMPAGR        7/CXC 146 1765/5000    R1A03        157   2   2
RHTRHR        7/CXC 146 1766/5000    R1A01        132   1   1
RHLAPDR       7/CXC 146 1691/4000    R1A04        283   0   0


RP    TYPE     TWIN
  78  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  79  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPIFDR        9000/CXC 146 03        R1A08          8  31
RPFDR         9000/CXC 146 05        R1A03         10  30
INETR         9000/CXC 146 591       R6F01         82  29
GPEX2R        9000/CXC 146 256       R5G01         35  16
RTIPTRHR      7/CXC 146 1696/4000    R1A01        330   8   8
RCSCB2R       7/CXC 146 1690/4000    R1A02        101   7   7
RCLCCHR       7/CXC 146 1759/5000    R1A02        147   6   6
RQRCQSR       7/CXC 146 1763/5000    R1A02        153   5   5
RQUNCR        7/CXC 146 1693/4000    R1A01        307   4   4
RCSCBR        7/CXC 146 1689/4000    R1A04        107   3   3
RMPAGR        7/CXC 146 1765/5000    R1A03        157   2   2
RHTRHR        7/CXC 146 1766/5000    R1A01        132   1   1
RHLAPDR       7/CXC 146 1691/4000    R1A04        283   0   0


RP    TYPE     TWIN
  80  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  81  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  82  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  83  GARP2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 05        R1A03         10  31
RPIFDR        9000/CXC 146 03        R1A08          8  30
INETR         9000/CXC 146 591       R6F01         82  29
SFRAMER       9000/CXC 146 48        R1C02         95  28
GPEX2R        9000/CXC 146 256       R5G01         35  16
ROFWR         7/CXC 146 1726/4000    R1A04        297  15  15
RCCBCR        7/CXC 146 1732/4000    R1A02         92  11  11
RGNCCR        7/CXC 146 1733/4000    R1A03        273  10  10
RTGBIPR       7/CXC 146 1755/5000    R1A06         96   9   9
RTIPGPHR      7/CXC 146 1712/4000    R1A01        324   8   8
RGCNTR        7/CXC 146 1748/P5046   P02A14       160   7   7
RGCONR        7/CXC 146 1749/P5046   P02A08       167   5   5
RGMACR        7/CXC 146 1750/5000    R1A72        148   4   4
RGRLCR        7/CXC 146 1747/5000    R1A11         88   3   3
RTGPHDVR      7/CXC 146 1734/4000    R1A01        319   2   2
RTGBR         7/CXC 146 1756/5000    R1A06        223   1   1
RGSERVR       7/CXC 146 1746/5000    R1A01        129   0   0


RP    TYPE     TWIN
  86  RPI2E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPIFDR        9000/CXC 146 23        R1A01         66  30
RIEXR         9000/CXC 146 147       R2L02         83  16
CLMR          9000/CXC 146 30        R1S01        114   0   0

END

'''

    rrscpAll = '''
rrscp:scgr=all;
RADIO TRANSMISSION SUPER CHANNEL DATA

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  20  0   RTPGD-3488     RBLT2-129      31        1  WO
      1   RTPGD-3255     RBLT2-472       8       56  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  23  0   RTPGD-3456     RBLT2-225      31        1  WO
      1   RTPGD-3223     RBLT2-257       8       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  25  0   RTPGD-3424     RBLT2-297      23        9  WO
      1   RTPGD-3232     RBLT2-321      23       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
  30  0   RTPGD-3392     RBLT2-449      23        1  WO
      1   RTPGD-3200     RBLT2-481      23       33  WO

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 100  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 101  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 102  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 103  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 104  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 105  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 106  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 107  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 108  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 109  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 110  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 120  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 121  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 122  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 123  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 124  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 125  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 126  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 127  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 128  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 129  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
 130  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1811  0   RTPGD-3360     RBLT2-4033     31        1  FLT    H'0000 0008
      1   RTPGD-3168     RBLT2-4065     31       33  FLT    H'0000 0008

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1813  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1823  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1831  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1832  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1833  0   RTPGD-3328     RBLT2-4289     31        1  FLT    H'0000 0008
      1   RTPGD-3136     RBLT2-4321     31       33  FLT    H'0000 0008

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1842  0   RTPGD-3296     RBLT2-4417     31        1  FLT    H'0000 0008
      1   RTPGD-3104     RBLT2-4449     31       33  FLT    H'0000 0008

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1843  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1871  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1872  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1873  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1881  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1882  0                                 31        1
      1                                 31       33
      2                                 31      287
      3                                 31      319

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1883  0                                 31        1
      1                                 31       33

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1902  0   RTPGD-3264     RBLT2-5249     31        1  FLT    H'0000 0008
      1   RTPGD-3073     RBLT2-5281     31       33  FLT    H'0000 0008

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1911  0                                 31        1

SCGR  SC  DEV            DEV1           NUMDEV  DCP  STATE  REASON
1912  0                                 31        1

END
'''

    rrntp = '''
RRNTP;
NODE TYPE DATA

NODETYPE  DPC    NEI
BSCTRC
END

'''

    rlsvpAllBCCHPS = '''
RLSVP:CELL=ALL,PSVTYPE=BCCHPS;
CELL POWER SAVINGS DATA

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
112C202  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
111C201  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
092C188  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
091C187  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
092C186  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
091C185  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
082C180  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
082C179  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
082C178  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
081C177  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
072C172  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
072C171  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
072C170  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
071C169  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
042C144  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
042C143  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
042C142  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
041C141  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
032C134  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
032C133  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
032C132  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
031C131  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
022C124  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
022C123  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
021C122  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
021C121  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
012C114  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
012C113  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
011C112  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
011C111  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150190  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150189  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150188  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150187  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150186  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150185  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150184  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150183  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150182  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150181  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150180  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150179  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150178  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150177  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150176  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150175  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150174  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150173  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150172  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150171  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150170  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150169  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150168  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150167  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150166  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150165  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150164  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150163  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150162  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150161  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1150160  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115070C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115070B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115070A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115069C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115069B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115069A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115068C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115068B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115068A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115067C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115067B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115067A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115066C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115066B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115066A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115065C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115065B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115065A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115064C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115064B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115064A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115063A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115062C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115062B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115062A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115061C  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115061B  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115061A  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115060C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115060B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115060A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115050C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115050B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115050A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115049C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115049B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115049A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115048C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115048B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115048A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115047C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115047B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115047A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115046C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115046B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115046A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115045C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115045B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115045A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115044C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115044B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115044A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115043A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115042C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115042B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115042A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115041C  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115041B  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115041A  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115040C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115040B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115040A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115030C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115030B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115030A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115029C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115029B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115029A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115028C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115028B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115028A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115027C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115027B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115027A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115026C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115026B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115026A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115025C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115025B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115025A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115024C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115024B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115024A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115023A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115022C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115022B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115022A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115021C  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115021B  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115021A  ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115020C  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115020B  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
115020A  INACTIVE  PCPR

         PRECCCH  PRO
         YES        1

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1152C7   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1152C6   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1152C5   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1152C4   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1152C3   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1152C2   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1152C1   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1151C7   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1151C6   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1151C5   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1151C4   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1151C3   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1151C2   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

CELL     BCCHPS    BCCHPSTYPE  BCCHPSST
1151C1   ACTIVE    PCPR

         PRECCCH  PRO
         YES        2

END

'''

    rlcrpCell = '''
rlcrp:cell=1150169;
CELL RESOURCES

CELL      BCCH  CBCH  SDCCH  NOOFTCH  QUEUED  ECBCCH
1150169      1     1     11  188-376       0       0

CHGR
 0
BPC   CHANNEL      CHRATE  SPV    STATE  ICMBAND  CHBAND  64K     USE
32750 SDCCH-221104                IDLE   1        P900
      SDCCH-221103                IDLE   1        P900
      SDCCH-221102                IDLE   1        P900
      SDCCH-221101                IDLE   1        P900
      BCCH-221100                 BUSY            P900
32726 SDCCH-221033                IDLE   1        P900
      SDCCH-221032                IDLE   1        P900
      CBCH-221031                 BUSY            P900
      SDCCH-221030                IDLE   1        P900
      SDCCH-221029                IDLE   1        P900
      SDCCH-221028                IDLE   1        P900
      SDCCH-221027                IDLE   1        P900
      SDCCH-221026                IDLE   1        P900
32675 TCH-220772   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220771   HR      1,3    IDLE   1        P900
      TCH-220770   HR      1,3    IDLE   1        P900
      TCH-220769   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220768   HR      1,3    IDLE   1        P900
      TCH-220767   HR      1,3    IDLE   1        P900
32530 TCH-220056   FR      1,2,   IDLE   1        P900    NONE
                           3,5
      TCH-220055   HR      1,3    IDLE   1        P900
      TCH-220054   HR      1,3    IDLE   1        P900
      TCH-220053   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220052   HR      1,3    IDLE   1        P900
      TCH-220051   HR      1,3    IDLE   1        P900
32584 TCH-220215   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220214   HR      1,3    IDLE   1        P900
      TCH-220213   HR      1,3    IDLE   1        P900
      TCH-220212   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220211   HR      1,3    IDLE   1        P900
      TCH-220210   HR      1,3    IDLE   1        P900
32608 TCH-220392   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220391   HR      1,3    IDLE   1        P900
      TCH-220390   HR      1,3    IDLE   1        P900
      TCH-220389   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220388   HR      1,3    IDLE   1        P900
      TCH-220387   HR      1,3    IDLE   1        P900
32632 TCH-220506   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220505   HR      1,3    IDLE   1        P900
      TCH-220504   HR      1,3    IDLE   1        P900
      TCH-220503   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220502   HR      1,3    IDLE   1        P900
      TCH-220501   HR      1,3    IDLE   1        P900
32654 TCH-220613   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220612   HR      1,3    IDLE   1        P900
      TCH-220611   HR      1,3    IDLE   1        P900
      TCH-220610   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220609   HR      1,3    IDLE   1        P900
      TCH-220608   HR      1,3    IDLE   1        P900
32408 TCH-219603   FR      1,2,   IDLE   1        P900    NONE
                           3,5
      TCH-219602   HR      1,3    IDLE   1        P900
      TCH-219601   HR      1,3    IDLE   1        P900
      TCH-219600   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219599   HR      1,3    IDLE   1        P900
      TCH-219598   HR      1,3    IDLE   1        P900
32437 TCH-219666   FR      1,2,   IDLE   1        P900    NONE
                           3,5
      TCH-219665   HR      1,3    IDLE   1        P900
      TCH-219664   HR      1,3    IDLE   1        P900
      TCH-219663   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219662   HR      1,3    IDLE   1        P900
      TCH-219661   HR      1,3    IDLE   1        P900
32462 TCH-219693   FR      1,2,   IDLE   1        P900    NONE
                           3,5
      TCH-219692   HR      1,3    IDLE   1        P900
      TCH-219691   HR      1,3    IDLE   1        P900
      TCH-219690   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219689   HR      1,3    IDLE   1        P900
      TCH-219688   HR      1,3    IDLE   1        P900
32549 TCH-220119   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220118   HR      1,3    IDLE   1        P900
      TCH-220117   HR      1,3    IDLE   1        P900
      TCH-220116   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220115   HR      1,3    IDLE   1        P900
      TCH-220114   HR      1,3    IDLE   1        P900
32560 TCH-220137   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220136   HR      1,3    IDLE   1        P900
      TCH-220135   HR      1,3    IDLE   1        P900
      TCH-220134   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220133   HR      1,3    IDLE   1        P900
      TCH-220132   HR      1,3    IDLE   1        P900
32568 TCH-220146   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-220145   HR      1,3    IDLE   1        P900
      TCH-220144   HR      1,3    IDLE   1        P900
      TCH-220143   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-220142   HR      1,3    IDLE   1        P900
      TCH-220141   HR      1,3    IDLE   1        P900
32489 TCH-219828   FR      1,2,   IDLE   1        P900    NONE
                           3,5
      TCH-219827   HR      1,3    IDLE   1        P900
      TCH-219826   HR      1,3    IDLE   1        P900
      TCH-219825   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219824   HR      1,3    IDLE   1        P900
      TCH-219823   HR      1,3    IDLE   1        P900
32511 TCH-219888   FR      1,2,   IDLE   1        P900    NONE
                           3,5
      TCH-219887   HR      1,3    IDLE   1        P900
      TCH-219886   HR      1,3    IDLE   1        P900
      TCH-219885   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219884   HR      1,3    IDLE   1        P900
      TCH-219883   HR      1,3    IDLE   1        P900

CHGR
 1
BPC   CHANNEL      CHRATE  SPV    STATE  ICMBAND  CHBAND  64K     USE
31968 TCH-217446   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217445   HR      1,3    IDLE   1        P900
      TCH-217444   HR      1,3    IDLE   1        P900
      TCH-217443   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217442   HR      1,3    IDLE   1        P900
      TCH-217441   HR      1,3    IDLE   1        P900
31969 TCH-217452   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217451   HR      1,3    IDLE   1        P900
      TCH-217450   HR      1,3    IDLE   1        P900
      TCH-217449   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217448   HR      1,3    IDLE   1        P900
      TCH-217447   HR      1,3    IDLE   1        P900
31978 TCH-217458   FR      1,2,   BUSY   1        P900    IAN     GPRS
                           3,5
      TCH-217457   HR      1,3    LOCK   1        P900
      TCH-217456   HR      1,3    LOCK   1        P900
      TCH-217455   FR      1,2,   LOCK   1        P900
                           3,5
      TCH-217454   HR      1,3    LOCK   1        P900
      TCH-217453   HR      1,3    LOCK   1        P900
31979 TCH-217464   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217463   HR      1,3    IDLE   1        P900
      TCH-217462   HR      1,3    IDLE   1        P900
      TCH-217461   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217460   HR      1,3    IDLE   1        P900
      TCH-217459   HR      1,3    IDLE   1        P900
31970 TCH-217470   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217469   HR      1,3    IDLE   1        P900
      TCH-217468   HR      1,3    IDLE   1        P900
      TCH-217467   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217466   HR      1,3    IDLE   1        P900
      TCH-217465   HR      1,3    IDLE   1        P900
31971 TCH-217476   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217475   HR      1,3    IDLE   1        P900
      TCH-217474   HR      1,3    IDLE   1        P900
      TCH-217473   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217472   HR      1,3    IDLE   1        P900
      TCH-217471   HR      1,3    IDLE   1        P900
31988 TCH-217482   FR      1,2,   BUSY   1        P900    IAN     GPRS
                           3,5
      TCH-217481   HR      1,3    LOCK   1        P900
      TCH-217480   HR      1,3    LOCK   1        P900
      TCH-217479   FR      1,2,   LOCK   1        P900
                           3,5
      TCH-217478   HR      1,3    LOCK   1        P900
      TCH-217477   HR      1,3    LOCK   1        P900
31989 TCH-217488   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217487   HR      1,3    IDLE   1        P900
      TCH-217486   HR      1,3    IDLE   1        P900
      TCH-217485   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217484   HR      1,3    IDLE   1        P900
      TCH-217483   HR      1,3    IDLE   1        P900
31980 TCH-217494   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217493   HR      1,3    IDLE   1        P900
      TCH-217492   HR      1,3    IDLE   1        P900
      TCH-217491   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217490   HR      1,3    IDLE   1        P900
      TCH-217489   HR      1,3    IDLE   1        P900
31981 TCH-217500   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217499   HR      1,3    IDLE   1        P900
      TCH-217498   HR      1,3    IDLE   1        P900
      TCH-217497   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217496   HR      1,3    IDLE   1        P900
      TCH-217495   HR      1,3    IDLE   1        P900
31998 TCH-217506   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217505   HR      1,3    IDLE   1        P900
      TCH-217504   HR      1,3    IDLE   1        P900
      TCH-217503   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217502   HR      1,3    IDLE   1        P900
      TCH-217501   HR      1,3    IDLE   1        P900
31990 TCH-217512   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217511   HR      1,3    IDLE   1        P900
      TCH-217510   HR      1,3    IDLE   1        P900
      TCH-217509   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217508   HR      1,3    IDLE   1        P900
      TCH-217507   HR      1,3    IDLE   1        P900
31999 TCH-217518   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217517   HR      1,3    IDLE   1        P900
      TCH-217516   HR      1,3    IDLE   1        P900
      TCH-217515   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217514   HR      1,3    IDLE   1        P900
      TCH-217513   HR      1,3    IDLE   1        P900
31991 TCH-217524   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217523   HR      1,3    IDLE   1        P900
      TCH-217522   HR      1,3    IDLE   1        P900
      TCH-217521   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217520   HR      1,3    IDLE   1        P900
      TCH-217519   HR      1,3    IDLE   1        P900
31972 TCH-217530   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217529   HR      1,3    IDLE   1        P900
      TCH-217528   HR      1,3    IDLE   1        P900
      TCH-217527   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217526   HR      1,3    IDLE   1        P900
      TCH-217525   HR      1,3    IDLE   1        P900
31973 TCH-217542   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217541   HR      1,3    IDLE   1        P900
      TCH-217540   HR      1,3    IDLE   1        P900
      TCH-217539   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217538   HR      1,3    IDLE   1        P900
      TCH-217537   HR      1,3    IDLE   1        P900
32008 TCH-217548   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217547   HR      1,3    IDLE   1        P900
      TCH-217546   HR      1,3    IDLE   1        P900
      TCH-217545   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217544   HR      1,3    IDLE   1        P900
      TCH-217543   HR      1,3    IDLE   1        P900
32000 TCH-217554   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217553   HR      1,3    IDLE   1        P900
      TCH-217552   HR      1,3    IDLE   1        P900
      TCH-217551   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217550   HR      1,3    IDLE   1        P900
      TCH-217549   HR      1,3    IDLE   1        P900
32001 TCH-217560   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217559   HR      1,3    IDLE   1        P900
      TCH-217558   HR      1,3    IDLE   1        P900
      TCH-217557   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217556   HR      1,3    IDLE   1        P900
      TCH-217555   HR      1,3    IDLE   1        P900
32009 TCH-217566   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217565   HR      1,3    IDLE   1        P900
      TCH-217564   HR      1,3    IDLE   1        P900
      TCH-217563   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217562   HR      1,3    IDLE   1        P900
      TCH-217561   HR      1,3    IDLE   1        P900
31982 TCH-217572   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217571   HR      1,3    IDLE   1        P900
      TCH-217570   HR      1,3    IDLE   1        P900
      TCH-217569   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217568   HR      1,3    IDLE   1        P900
      TCH-217567   HR      1,3    IDLE   1        P900
31983 TCH-217578   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217577   HR      1,3    IDLE   1        P900
      TCH-217576   HR      1,3    IDLE   1        P900
      TCH-217575   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217574   HR      1,3    IDLE   1        P900
      TCH-217573   HR      1,3    IDLE   1        P900
31974 TCH-217584   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217583   HR      1,3    IDLE   1        P900
      TCH-217582   HR      1,3    IDLE   1        P900
      TCH-217581   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217580   HR      1,3    IDLE   1        P900
      TCH-217579   HR      1,3    IDLE   1        P900
31975 TCH-217608   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217607   HR      1,3    IDLE   1        P900
      TCH-217606   HR      1,3    IDLE   1        P900
      TCH-217605   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217604   HR      1,3    IDLE   1        P900
      TCH-217603   HR      1,3    IDLE   1        P900
32010 TCH-217614   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217613   HR      1,3    IDLE   1        P900
      TCH-217612   HR      1,3    IDLE   1        P900
      TCH-217611   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217610   HR      1,3    IDLE   1        P900
      TCH-217609   HR      1,3    IDLE   1        P900
31976 TCH-217620   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217619   HR      1,3    IDLE   1        P900
      TCH-217618   HR      1,3    IDLE   1        P900
      TCH-217617   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217616   HR      1,3    IDLE   1        P900
      TCH-217615   HR      1,3    IDLE   1        P900
32018 TCH-217626   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217625   HR      1,3    IDLE   1        P900
      TCH-217624   HR      1,3    IDLE   1        P900
      TCH-217623   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217622   HR      1,3    IDLE   1        P900
      TCH-217621   HR      1,3    IDLE   1        P900
32019 TCH-217632   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217631   HR      1,3    IDLE   1        P900
      TCH-217630   HR      1,3    IDLE   1        P900
      TCH-217629   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217628   HR      1,3    IDLE   1        P900
      TCH-217627   HR      1,3    IDLE   1        P900
31984 TCH-217638   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217637   HR      1,3    IDLE   1        P900
      TCH-217636   HR      1,3    IDLE   1        P900
      TCH-217635   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217634   HR      1,3    IDLE   1        P900
      TCH-217633   HR      1,3    IDLE   1        P900
31977 TCH-217644   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217643   HR      1,3    IDLE   1        P900
      TCH-217642   HR      1,3    IDLE   1        P900
      TCH-217641   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217640   HR      1,3    IDLE   1        P900
      TCH-217639   HR      1,3    IDLE   1        P900
31992 TCH-217650   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217649   HR      1,3    IDLE   1        P900
      TCH-217648   HR      1,3    IDLE   1        P900
      TCH-217647   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217646   HR      1,3    IDLE   1        P900
      TCH-217645   HR      1,3    IDLE   1        P900
31993 TCH-217656   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217655   HR      1,3    IDLE   1        P900
      TCH-217654   HR      1,3    IDLE   1        P900
      TCH-217653   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217652   HR      1,3    IDLE   1        P900
      TCH-217651   HR      1,3    IDLE   1        P900
32011 TCH-217662   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217661   HR      1,3    IDLE   1        P900
      TCH-217660   HR      1,3    IDLE   1        P900
      TCH-217659   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217658   HR      1,3    IDLE   1        P900
      TCH-217657   HR      1,3    IDLE   1        P900
31985 TCH-217680   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217679   HR      1,3    IDLE   1        P900
      TCH-217678   HR      1,3    IDLE   1        P900
      TCH-217677   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217676   HR      1,3    IDLE   1        P900
      TCH-217675   HR      1,3    IDLE   1        P900
31986 TCH-217692   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217691   HR      1,3    IDLE   1        P900
      TCH-217690   HR      1,3    IDLE   1        P900
      TCH-217689   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217688   HR      1,3    IDLE   1        P900
      TCH-217687   HR      1,3    IDLE   1        P900
31987 TCH-217698   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217697   HR      1,3    IDLE   1        P900
      TCH-217696   HR      1,3    IDLE   1        P900
      TCH-217695   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217694   HR      1,3    IDLE   1        P900
      TCH-217693   HR      1,3    IDLE   1        P900
32020 TCH-217704   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217703   HR      1,3    IDLE   1        P900
      TCH-217702   HR      1,3    IDLE   1        P900
      TCH-217701   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217700   HR      1,3    IDLE   1        P900
      TCH-217699   HR      1,3    IDLE   1        P900
31994 TCH-217716   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217715   HR      1,3    IDLE   1        P900
      TCH-217714   HR      1,3    IDLE   1        P900
      TCH-217713   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217712   HR      1,3    IDLE   1        P900
      TCH-217711   HR      1,3    IDLE   1        P900
31995 TCH-217728   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217727   HR      1,3    IDLE   1        P900
      TCH-217726   HR      1,3    IDLE   1        P900
      TCH-217725   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217724   HR      1,3    IDLE   1        P900
      TCH-217723   HR      1,3    IDLE   1        P900
32023 TCH-217734   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217733   HR      1,3    IDLE   1        P900
      TCH-217732   HR      1,3    IDLE   1        P900
      TCH-217731   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217730   HR      1,3    IDLE   1        P900
      TCH-217729   HR      1,3    IDLE   1        P900
32003 TCH-217746   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217745   HR      1,3    IDLE   1        P900
      TCH-217744   HR      1,3    IDLE   1        P900
      TCH-217743   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217742   HR      1,3    IDLE   1        P900
      TCH-217741   HR      1,3    IDLE   1        P900
32002 TCH-217752   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217751   HR      1,3    IDLE   1        P900
      TCH-217750   HR      1,3    IDLE   1        P900
      TCH-217749   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217748   HR      1,3    IDLE   1        P900
      TCH-217747   HR      1,3    IDLE   1        P900
31996 TCH-217770   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217769   HR      1,3    IDLE   1        P900
      TCH-217768   HR      1,3    IDLE   1        P900
      TCH-217767   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217766   HR      1,3    IDLE   1        P900
      TCH-217765   HR      1,3    IDLE   1        P900
31997 TCH-217782   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217781   HR      1,3    IDLE   1        P900
      TCH-217780   HR      1,3    IDLE   1        P900
      TCH-217779   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217778   HR      1,3    IDLE   1        P900
      TCH-217777   HR      1,3    IDLE   1        P900
32012 TCH-217806   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217805   HR      1,3    IDLE   1        P900
      TCH-217804   HR      1,3    IDLE   1        P900
      TCH-217803   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217802   HR      1,3    IDLE   1        P900
      TCH-217801   HR      1,3    IDLE   1        P900
32013 TCH-217812   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217811   HR      1,3    IDLE   1        P900
      TCH-217810   HR      1,3    IDLE   1        P900
      TCH-217809   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217808   HR      1,3    IDLE   1        P900
      TCH-217807   HR      1,3    IDLE   1        P900
32004 TCH-217818   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217817   HR      1,3    IDLE   1        P900
      TCH-217816   HR      1,3    IDLE   1        P900
      TCH-217815   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217814   HR      1,3    IDLE   1        P900
      TCH-217813   HR      1,3    IDLE   1        P900
32005 TCH-217842   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217841   HR      1,3    IDLE   1        P900
      TCH-217840   HR      1,3    IDLE   1        P900
      TCH-217839   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217838   HR      1,3    IDLE   1        P900
      TCH-217837   HR      1,3    IDLE   1        P900
32006 TCH-217860   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217859   HR      1,3    IDLE   1        P900
      TCH-217858   HR      1,3    IDLE   1        P900
      TCH-217857   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217856   HR      1,3    IDLE   1        P900
      TCH-217855   HR      1,3    IDLE   1        P900
32007 TCH-217875   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217874   HR      1,3    IDLE   1        P900
      TCH-217873   HR      1,3    IDLE   1        P900
      TCH-217872   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217871   HR      1,3    IDLE   1        P900
      TCH-217870   HR      1,3    IDLE   1        P900
32014 TCH-217881   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217880   HR      1,3    IDLE   1        P900
      TCH-217879   HR      1,3    IDLE   1        P900
      TCH-217878   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217877   HR      1,3    IDLE   1        P900
      TCH-217876   HR      1,3    IDLE   1        P900
32057 TCH-217890   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217889   HR      1,3    IDLE   1        P900
      TCH-217888   HR      1,3    IDLE   1        P900
      TCH-217887   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217886   HR      1,3    IDLE   1        P900
      TCH-217885   HR      1,3    IDLE   1        P900
32031 TCH-217896   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217895   HR      1,3    IDLE   1        P900
      TCH-217894   HR      1,3    IDLE   1        P900
      TCH-217893   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217892   HR      1,3    IDLE   1        P900
      TCH-217891   HR      1,3    IDLE   1        P900
32027 TCH-217902   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217901   HR      1,3    IDLE   1        P900
      TCH-217900   HR      1,3    IDLE   1        P900
      TCH-217899   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217898   HR      1,3    IDLE   1        P900
      TCH-217897   HR      1,3    IDLE   1        P900
32015 TCH-217917   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217916   HR      1,3    IDLE   1        P900
      TCH-217915   HR      1,3    IDLE   1        P900
      TCH-217914   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217913   HR      1,3    IDLE   1        P900
      TCH-217912   HR      1,3    IDLE   1        P900
32016 TCH-217944   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217943   HR      1,3    IDLE   1        P900
      TCH-217942   HR      1,3    IDLE   1        P900
      TCH-217941   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217940   HR      1,3    IDLE   1        P900
      TCH-217939   HR      1,3    IDLE   1        P900
32017 TCH-217950   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217949   HR      1,3    IDLE   1        P900
      TCH-217948   HR      1,3    IDLE   1        P900
      TCH-217947   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217946   HR      1,3    IDLE   1        P900
      TCH-217945   HR      1,3    IDLE   1        P900
32052 TCH-217968   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-217967   HR      1,3    IDLE   1        P900
      TCH-217966   HR      1,3    IDLE   1        P900
      TCH-217965   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-217964   HR      1,3    IDLE   1        P900
      TCH-217963   HR      1,3    IDLE   1        P900
32036 TCH-218028   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218027   HR      1,3    IDLE   1        P900
      TCH-218026   HR      1,3    IDLE   1        P900
      TCH-218025   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218024   HR      1,3    IDLE   1        P900
      TCH-218023   HR      1,3    IDLE   1        P900
32064 TCH-218049   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218048   HR      1,3    IDLE   1        P900
      TCH-218047   HR      1,3    IDLE   1        P900
      TCH-218046   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218045   HR      1,3    IDLE   1        P900
      TCH-218044   HR      1,3    IDLE   1        P900
32040 TCH-218067   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218066   HR      1,3    IDLE   1        P900
      TCH-218065   HR      1,3    IDLE   1        P900
      TCH-218064   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218063   HR      1,3    IDLE   1        P900
      TCH-218062   HR      1,3    IDLE   1        P900
32070 TCH-218073   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218072   HR      1,3    IDLE   1        P900
      TCH-218071   HR      1,3    IDLE   1        P900
      TCH-218070   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218069   HR      1,3    IDLE   1        P900
      TCH-218068   HR      1,3    IDLE   1        P900
32044 TCH-218091   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218090   HR      1,3    IDLE   1        P900
      TCH-218089   HR      1,3    IDLE   1        P900
      TCH-218088   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218087   HR      1,3    IDLE   1        P900
      TCH-218086   HR      1,3    IDLE   1        P900
32048 TCH-218136   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218135   HR      1,3    IDLE   1        P900
      TCH-218134   HR      1,3    IDLE   1        P900
      TCH-218133   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218132   HR      1,3    IDLE   1        P900
      TCH-218131   HR      1,3    IDLE   1        P900
32090 TCH-218328   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218327   HR      1,3    IDLE   1        P900
      TCH-218326   HR      1,3    IDLE   1        P900
      TCH-218325   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218324   HR      1,3    IDLE   1        P900
      TCH-218323   HR      1,3    IDLE   1        P900
32099 TCH-218340   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218339   HR      1,3    IDLE   1        P900
      TCH-218338   HR      1,3    IDLE   1        P900
      TCH-218337   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218336   HR      1,3    IDLE   1        P900
      TCH-218335   HR      1,3    IDLE   1        P900
32106 TCH-218346   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218345   HR      1,3    IDLE   1        P900
      TCH-218344   HR      1,3    IDLE   1        P900
      TCH-218343   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218342   HR      1,3    IDLE   1        P900
      TCH-218341   HR      1,3    IDLE   1        P900
32076 TCH-218397   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218396   HR      1,3    IDLE   1        P900
      TCH-218395   HR      1,3    IDLE   1        P900
      TCH-218394   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218393   HR      1,3    IDLE   1        P900
      TCH-218392   HR      1,3    IDLE   1        P900
32082 TCH-218403   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218402   HR      1,3    IDLE   1        P900
      TCH-218401   HR      1,3    IDLE   1        P900
      TCH-218400   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218399   HR      1,3    IDLE   1        P900
      TCH-218398   HR      1,3    IDLE   1        P900
32114 TCH-218442   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218441   HR      1,3    IDLE   1        P900
      TCH-218440   HR      1,3    IDLE   1        P900
      TCH-218439   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218438   HR      1,3    IDLE   1        P900
      TCH-218437   HR      1,3    IDLE   1        P900
32123 TCH-218448   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218447   HR      1,3    IDLE   1        P900
      TCH-218446   HR      1,3    IDLE   1        P900
      TCH-218445   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218444   HR      1,3    IDLE   1        P900
      TCH-218443   HR      1,3    IDLE   1        P900
32134 TCH-218532   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218531   HR      1,3    IDLE   1        P900
      TCH-218530   HR      1,3    IDLE   1        P900
      TCH-218529   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218528   HR      1,3    IDLE   1        P900
      TCH-218527   HR      1,3    IDLE   1        P900
32147 TCH-218550   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218549   HR      1,3    IDLE   1        P900
      TCH-218548   HR      1,3    IDLE   1        P900
      TCH-218547   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218546   HR      1,3    IDLE   1        P900
      TCH-218545   HR      1,3    IDLE   1        P900
32162 TCH-218580   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218579   HR      1,3    IDLE   1        P900
      TCH-218578   HR      1,3    IDLE   1        P900
      TCH-218577   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218576   HR      1,3    IDLE   1        P900
      TCH-218575   HR      1,3    IDLE   1        P900
32174 TCH-218709   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218708   HR      1,3    IDLE   1        P900
      TCH-218707   HR      1,3    IDLE   1        P900
      TCH-218706   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218705   HR      1,3    IDLE   1        P900
      TCH-218704   HR      1,3    IDLE   1        P900
32190 TCH-218727   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218726   HR      1,3    IDLE   1        P900
      TCH-218725   HR      1,3    IDLE   1        P900
      TCH-218724   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218723   HR      1,3    IDLE   1        P900
      TCH-218722   HR      1,3    IDLE   1        P900
32203 TCH-218919   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-218918   HR      1,3    IDLE   1        P900
      TCH-218917   HR      1,3    IDLE   1        P900
      TCH-218916   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-218915   HR      1,3    IDLE   1        P900
      TCH-218914   HR      1,3    IDLE   1        P900
32220 TCH-219063   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-219062   HR      1,3    IDLE   1        P900
      TCH-219061   HR      1,3    IDLE   1        P900
      TCH-219060   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219059   HR      1,3    IDLE   1        P900
      TCH-219058   HR      1,3    IDLE   1        P900
32241 TCH-219186   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-219185   HR      1,3    IDLE   1        P900
      TCH-219184   HR      1,3    IDLE   1        P900
      TCH-219183   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219182   HR      1,3    IDLE   1        P900
      TCH-219181   HR      1,3    IDLE   1        P900
32302 TCH-219303   FR      1,2,   IDLE   1        P900    IAN
                           3,5
      TCH-219302   HR      1,3    IDLE   1        P900
      TCH-219301   HR      1,3    IDLE   1        P900
      TCH-219300   FR      1,2,   IDLE   1        P900
                           3,5
      TCH-219299   HR      1,3    IDLE   1        P900
      TCH-219298   HR      1,3    IDLE   1        P900
END

'''


    iougp = '''
IOUGp;
MCS AUTHORITY USER GROUP TABLE

USERGR     0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15

CATEGORIES
  0&&63    1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
 64        1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
 65&&255   0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0

END
'''

    sastp = '''
SASTP;

STORE UTILIZATION

ITEM                                PS               RS               DS

TOTAL ALLOCATED AREAS            46972             2607          2180237
TOTAL FREE AREAS                 82365            13770          1569850
TRANSPORT AREA                    1733                6
TOTAL BACKUP AREA                                                 171576

LOGICAL STORE                   131070            16383          3750087
PHYSICAL STORE                  131070            16383          3921663

WORD LENGTH                         16               32               16


UNITS         ADDRUNIT
KW            LOGICAL

END
'''

    ntcopSnt = '''
ntcop:snt=RTAGWS-1;
SWITCHING NETWORK TERMINAL CONNECTION DATA

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTAGWS-1          1 XM-0-1-12           RTAGWD-1024&&-2047

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTAGWS-1                                                XM-0-1-12   1024
END
'''

    ntcopAll = '''
NTCOP:SNT=All;
SWITCHING NETWORK TERMINAL CONNECTION DATA

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
ETM2-0            1 XM-0-0-7    4RBLT   RBLT2-128&&-159            20
                                5RBLT   RBLT2-160&&-191            21
                                6RBLT   RBLT2-192&&-223            22
                                7RBLT   RBLT2-224&&-255            23
                                8RBLT   RBLT2-256&&-287            24
                                9RBLT   RBLT2-288&&-319            25
                                10RBLT  RBLT2-320&&-351            26
                                11RBLT  RBLT2-352&&-383            27
                                12RBLT  RBLT2-384&&-415            28
                                13RBLT  RBLT2-416&&-447            29
                                14RBLT  RBLT2-448&&-479            30
                                15RBLT  RBLT2-480&&-511            31
                                120RBLT RBLT2-3840&&-3871          32
                                121RBLT RBLT2-3872&&-3903          33
                                122RBLT RBLT2-3904&&-3935          34
                                123RBLT RBLT2-3936&&-3967          35
                                16RBLT  RBLT2-512&&-543            36
                                17RBLT  RBLT2-544&&-575            37
                                18RBLT  RBLT2-576&&-607            38
                                19RBLT  RBLT2-608&&-639            39
                                20RBLT  RBLT2-640&&-671            40
                                21RBLT  RBLT2-672&&-703            41
                                22RBLT  RBLT2-704&&-735            42
                                23RBLT  RBLT2-736&&-767            43
                                24RBLT  RBLT2-768&&-799            44
                                25RBLT  RBLT2-800&&-831            45
                                26RBLT  RBLT2-832&&-863            46
                                27RBLT  RBLT2-864&&-895            47
                                0RBLT   RBLT2-0&&-31               52
                                1RBLT   RBLT2-32&&-63              53
                                2RBLT   RBLT2-64&&-95              54
                                3RBLT   RBLT2-96&&-127             55
                                100RBLT RBLT2-3200&&-3231          56
                                101RBLT RBLT2-3232&&-3263          57
                                102RBLT RBLT2-3264&&-3295          58
                                103RBLT RBLT2-3296&&-3327          59
                                0RTGLT  RTGLT2-0&&-31              60
                                1RTGLT  RTGLT2-32&&-63             61
                                0RTLBT  RTLBT2-0&&-31              62


SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
ETM2-0                    0      0ETM2   0              XM-0-0-7    2048

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
ETM2-2            1 XM-0-0-18   126RBLT RBLT2-4032&&-4063           0
                                127RBLT RBLT2-4064&&-4095           1
                                128RBLT RBLT2-4096&&-4127           2
                                129RBLT RBLT2-4128&&-4159           3
                                130RBLT RBLT2-4160&&-4191           4
                                131RBLT RBLT2-4192&&-4223           5
                                132RBLT RBLT2-4224&&-4255           6
                                133RBLT RBLT2-4256&&-4287           7
                                134RBLT RBLT2-4288&&-4319           8
                                135RBLT RBLT2-4320&&-4351           9
                                136RBLT RBLT2-4352&&-4383          10
                                137RBLT RBLT2-4384&&-4415          11
                                138RBLT RBLT2-4416&&-4447          12
                                139RBLT RBLT2-4448&&-4479          13
                                140RBLT RBLT2-4480&&-4511          14
                                141RBLT RBLT2-4512&&-4543          15
                                142RBLT RBLT2-4544&&-4575          16
                                143RBLT RBLT2-4576&&-4607          17
                                144RBLT RBLT2-4608&&-4639          18
                                145RBLT RBLT2-4640&&-4671          19
                                146RBLT RBLT2-4672&&-4703          20
                                147RBLT RBLT2-4704&&-4735          21
                                148RBLT RBLT2-4736&&-4767          22
                                149RBLT RBLT2-4768&&-4799          23
                                150RBLT RBLT2-4800&&-4831          24
                                151RBLT RBLT2-4832&&-4863          25
                                152RBLT RBLT2-4864&&-4895          26
                                153RBLT RBLT2-4896&&-4927          27
                                154RBLT RBLT2-4928&&-4959          28
                                155RBLT RBLT2-4960&&-4991          29
                                156RBLT RBLT2-4992&&-5023          30
                                157RBLT RBLT2-5024&&-5055          31
                                158RBLT RBLT2-5056&&-5087          32
                                159RBLT RBLT2-5088&&-5119          33
                                160RBLT RBLT2-5120&&-5151          34
                                161RBLT RBLT2-5152&&-5183          35
                                162RBLT RBLT2-5184&&-5215          36
                                163RBLT RBLT2-5216&&-5247          37
                                164RBLT RBLT2-5248&&-5279          38
                                165RBLT RBLT2-5280&&-5311          39
                                166RBLT RBLT2-5312&&-5343          40
                                167RBLT RBLT2-5344&&-5375          41
                                168RBLT RBLT2-5376&&-5407          42
                                169RBLT RBLT2-5408&&-5439          43
                                170RBLT RBLT2-5440&&-5471          44
                                171RBLT RBLT2-5472&&-5503          45
                                172RBLT RBLT2-5504&&-5535          46
                                173RBLT RBLT2-5536&&-5567          47
                                174RBLT RBLT2-5568&&-5599          48
                                175RBLT RBLT2-5600&&-5631          49
                                176RBLT RBLT2-5632&&-5663          50
                                177RBLT RBLT2-5664&&-5695          51
                                178RBLT RBLT2-5696&&-5727          52
                                179RBLT RBLT2-5728&&-5759          53
                                180RBLT RBLT2-5760&&-5791          54
                                181RBLT RBLT2-5792&&-5823          55
                                182RBLT RBLT2-5824&&-5855          56
                                183RBLT RBLT2-5856&&-5887          57
                                184RBLT RBLT2-5888&&-5919          58
                                185RBLT RBLT2-5920&&-5951          59
                                186RBLT RBLT2-5952&&-5983          60
                                187RBLT RBLT2-5984&&-6015          61
                                188RBLT RBLT2-6016&&-6047          62


SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
ETM2-2                    0      2ETM2   0              XM-0-0-18   2048

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTPGS-0           2 XM-0-0-4            RTPGD-0&&-1023

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTPGS-0                                                 XM-0-0-4    1024

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTPGS-1           2 XM-0-0-11           RTPGD-1024&&-2047

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTPGS-1                                                 XM-0-0-11   1024

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTPGS-2           2 XM-0-0-5            RTPGD-2048&&-3071

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTPGS-2                                                 XM-0-0-5    1024

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTPGS-3           2 XM-0-0-12           RTPGD-3072&&-4095

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTPGS-3                                                 XM-0-0-12   1024

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTPGS-4           2 XM-0-0-6            RTPGD-4096&&-5119

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTPGS-4                                                 XM-0-0-6    1024

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-0         2 XM-0-0-2            RTGPHDV-0&&-511

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-0                                               XM-0-0-2     512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-1         2 XM-0-0-13           RTGPHDV-512&&-1023

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-1                                               XM-0-0-13    512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-2         2 XM-0-0-3            RTGPHDV-1024&&-1535

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-2                                               XM-0-0-3     512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-3         2 XM-0-0-14           RTGPHDV-1536&&-2047

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-3                                               XM-0-0-14    512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-4         2 XM-0-1-4            RTGPHDV-2048&&-2559

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-4                                               XM-0-1-4     512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-5         2 XM-0-1-5            RTGPHDV-2560&&-3071

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-5                                               XM-0-1-5     512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-6         2 XM-0-1-6            RTGPHDV-3072&&-3583

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-6                                               XM-0-1-6     512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-7         2 XM-0-1-17           RTGPHDV-3584&&-4095

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-7                                               XM-0-1-17    512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTSNT34-8         2 XM-0-1-7            RTGPHDV-4096&&-4607

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTSNT34-8                                               XM-0-1-7     512

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RHSNT34-0         2 XM-0-1-13           RHDEV-0&&-255

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RHSNT34-0                                               XM-0-1-13    256

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RHSNT34-1         2 XM-0-1-14           RHDEV-256&&-511

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RHSNT34-1                                               XM-0-1-14    256

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RHSNT34-2         2 XM-0-1-15           RHDEV-512&&-767

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RHSNT34-2                                               XM-0-1-15    256

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RHSNT34-3         2 XM-0-1-16           RHDEV-768&&-1023

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RHSNT34-3                                               XM-0-1-16    256

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTAGWS-0          1 XM-0-1-11           RTAGWD-0&&-1023

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTAGWS-0                                                XM-0-1-11   1024

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTAGWS-1          1 XM-0-1-12           RTAGWD-1024&&-2047

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTAGWS-1                                                XM-0-1-12   1024

SNT           SNTV  SNTP        DIP     DEV                       SNTINL
RTAGWS-2          1 XM-0-1-18           RTAGWD-2048&&-3071

SNT                 EQLEV PROT   SDIP    SUBSNT DEFPST  SNTP        MODE
RTAGWS-2                                                XM-0-1-18   1024
END

'''
    ihpgpAll = '''IHPGP:PGID=ALL;
SCTP PG CONFIGURATION PARAMETERS DATA

PGID    PGNAME
0

RTOI       RTOMI      RTOMA
5000       1000       5000
200        100        400

SM         QSMIT      QSMAT      CPM        BIS
2          65535      65535      1          0
2          1          120        1          0

ARW        BUF        CATHR      COTHR
65535      2048       100        100
32768      256        40         50

HBS        HBI        LBS        LBT
DISABLED   1800       DISABLED   1000
ENABLED    30         ENABLED    10

MIS        MOS        TSACK      FSACK
65535      65535      500        2
17         17         40         2

DSCP       MTU        TZWND        VCL
63         65391      1            180
40         1416       1            60

AMR        IMR        SMR        PMR        PFMR
20         16         20         20         20
8          8          8          4          0

AICL       RTOA       RTOB       SSCWND
180        4          4          200
30         3          2          200


PGID    PGNAME
1

RTOI       RTOMI      RTOMA
-          -          -
200        100        400

SM         QSMIT      QSMAT      CPM        BIS
-          -          -          -          -
2          1          120        1          0

ARW        BUF        CATHR      COTHR
-          -          -          -
32768      256        40         50

HBS        HBI        LBS        LBT
-          -          -          -
ENABLED    30         ENABLED    10

MIS        MOS        TSACK      FSACK
-          17          -          -
17         17         40         2

DSCP       MTU        TZWND        VCL
-          -          -            60
40         1416       1            60

AMR        IMR        SMR        PMR        PFMR
-          8          -          -          1
8          8          8          4          0

AICL       RTOA       RTOB       SSCWND
30          2         2          -
30         3          2          200

END

'''

    ihrtpHostAll = '''
IHRTP:HOST=ALL;
DNS RESOLVER LOCAL TABLE DATA

LTID     HOST_NAME                       IPADDRESS
  0      NEPTUN.COM                      170.20.40.155
  1      NEPTUN.COM                      FA::4
  2      ODCON.COM                       170:128:168:126:210:123:115:25
  3      UKR.NET                         170.20.40.155

END

'''

    rlllpAll = '''
RLLLP:CELL=ALL;

SUBCELL LOAD DISTRIBUTION DATA

CELL     SCLD  SCLDLUL SCLDLOL SCLDSC
112C202  OFF   20      20      UL
111C201  OFF   20      20      UL
092C188  OFF   20      20      UL
091C187  OFF   20      20      UL
1151C7   OFF   20      20      UL
1151C6   OFF   20      20      UL
1151C5   OFF   20      20      UL
1151C4   OFF   20      20      UL
1151C3   OFF   20      20      UL
1151C2   OFF   20      20      UL
1151C1   ON    20      10      UL
END
'''

    rfimpAll = '''
rfimp:set=all;
PERMITTED IMSI SET DATA

BSCIMSIHO
ACTIVE

SET  NCCPERM          IMSIPAT
A    3 5 7            6666666
                      6646666
                      6661666
                      6666636
                      6664666

SET  NCCPERM          IMSIPAT
B

SET  NCCPERM          IMSIPAT
C

SET  NCCPERM          IMSIPAT
D

END
'''

    ihlpp = '''
IHLPP;
SCTP ON CP LAYER PARAMETERS DATA

NAS      HBI      RTOBF
0          30     28180

RBS         MSS   BUF      LBT
     32768  1416      256    10

PMR      HBS
  4      1

IMR      AMR      AICL     VCL
  8        8       30       60

RTOMI    RTOMA    RTOI     RTOA     RTOB     TSACK
 100      400      200     3        2         40

MIS      USER
 257     M3UA
8192     ASUA
   2     M2PA
 256     SUA
  16     GCP

PSS  PFMR  SM  QSMIT   QSMAT
1      0   1       8     120

END


'''


    ntstpAll = '''
ntstp:snt=all;
SWITCHING NETWORK TERMINAL STATE

SNT                STATE       BLS   LST              FCODE
RTPGS-0            WO          
RTPGS-1            WO          
RTPGS-2            WO          
RTPGS-3            WO          
RTPGS-4            WO          
RTSNT34-0          WO          
RTSNT34-1          WO          
RTSNT34-2          WO          
RTSNT34-3          WO          
RTSNT34-4          WO          
RTSNT34-5          WO          
RTSNT34-6          WO          
RTSNT34-7          WO          
RTSNT34-8          WO          
RHSNT34-0          WO          
RHSNT34-1          WO          
RHSNT34-2          WO          
RHSNT34-3          WO          
RTAGWS-0           WO          
RTAGWS-1           WO          
RTAGWS-2           WO          
SNT                SUBSNT  STATE     BLS LST              FCODE
ETM2-0                     WO        
                   0       WO            
ETM2-2                     WO        
                   0       WO

END
'''

    trtspMp = '''
TRTSP:MP=12;
TRAFFIC RECORDING TIME SCHEDULE

MP   NRP   RPL   DATE    NDAYS  DCAT  TIME    NWEEKS WEEKDAY
 12     1    60  160921  365    ALL   2300
        2    61                       2301
        3    62                       2302

END


'''

    syfsp = '''SYFSP;
FORLOPP EXECUTION STATUS

FORLOPP HANDLING
ACTIVE

FORLOPP EXECUTION CONTROL FUNCTION (ECF)
ON

BLOCK WITH ECF OFF
RTPRH
RHLAPD

FORLOPP ERROR FUNCTION (FLERROR)
ON

BLOCK WITH FLERROR OFF
RTTRINT

BLOCK WITH FLERROR ON
RTPGW

BLOCK WITH FLERROR TERM
RTPRH
RTPGS

FORLOPP AUDIT FUNCTION (FLAUDIT)

BLOCK WITH FLAUDIT OFF
RTPRH
RHLINK

FORLOPP MODE   SUBMODE        LIMIT
OPERATION2     FULL LOAD      90

END'''

    rxmopAllOTG = '''
rxmop:moty=rxotg;
RADIO X-CEIVER ADMINISTRATION
MANAGED OBJECT DATA

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-20          TG20                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       410         20

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0077   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-21          TG21                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   21

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0076   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-22          TG22                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       410         22

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0075   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-23          TG23                                FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   23

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0074   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-24          TG24                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   24

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0073   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-25          TG25                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   25

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0072   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-26          TG26                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   26

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0071   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-27          TG27                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       411         27

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0070   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-28          TG28                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       411         28

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-006F   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-29          TG29                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   29

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-006E   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-30          TG30                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                                 MG12R13A19V1   MG12R13A19V1  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   30

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-006D   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-40          TG40                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       420         40

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-006C   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-41          TG41                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   41

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-006B   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-42          TG42                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       420         42

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-006A   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-43          TG43                                FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   43

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0069   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-44          TG44                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   44

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0068   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-45          TG45                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   45

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0067   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-46          TG46                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   46

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0066   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-47          TG47                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       421         47

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0065   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-48          TG48                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       421         48

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0064   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-49          TG49                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   49

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0063   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-50          TG50                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   50

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0062   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-60          TG60                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       430         60

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0061   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-61          TG61                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   61

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0060   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-62          TG62                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       430         62

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-005F   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-63          TG63                                FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   63

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-005E   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-64          TG64                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   64

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-005D   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-65          TG65                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   65

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-005C   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-66          TG66                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   66

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-005B   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-67          TG67                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       431         67

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-005A   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-68          TG68                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       431         68

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0059   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-69          TG69                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   69

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0058   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-70          TG70                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   70

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0057   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-80          TG80                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       440         80

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0056   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-81          TG81                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   81

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0055   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-82          TG82                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       440         82

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0054   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-83          TG83                                FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   83

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0053   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-84          TG84                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   84

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0052   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-85          TG85                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                   85

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0051   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-86          TG86                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   86

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0050   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-87          TG87                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       441         87

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-004F   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-88          TG88                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       441         88

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-004E   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-89          TG89                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                   89

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-004D   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-90          TG90                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                   90

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-004C   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-100         TG100                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                                 MG12R13A19V1   MG12R13A19V1  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       450        100

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-004B   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-101         TG101                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  101

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-004A   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-102         TG102                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       450        102

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0049   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-103         TG103                               FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  103

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0048   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-104         TG104                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  104

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0047   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-105         TG105                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  105

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0046   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-106         TG106                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  106

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0045   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-107         TG107                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       451        107

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0044   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-108         TG108                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       451        108

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0043   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-109         TG109                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  109

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0042   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-110         TG110                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  110

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0041   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-120         TG120                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       460        120

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0040   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-121         TG121                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  121

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-003F   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-122         TG122                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       460        122

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-003E   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-123         TG123                               FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  123

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-003D   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-124         TG124                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  124

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-003C   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-125         TG125                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  125

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-003B   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-126         TG126                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  126

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-003A   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-127         TG127                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       461        127

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0039   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-128         TG128                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       461        128

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0038   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-129         TG129                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  129

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0037   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-130         TG130                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  130

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0036   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-140         TG140                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       470        140

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0035   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-141         TG141                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  141

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0034   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-142         TG142                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       470        142

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0033   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-143         TG143                               FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  143

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0032   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-144         TG144                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  144

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0031   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-145         TG145                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  145

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0030   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-146         TG146                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  146

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-002F   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-147         TG147                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       471        147

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-002E   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-148         TG148                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       471        148

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-002D   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-149         TG149                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  149

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-002C   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-150         TG150                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  150

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-002B   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-160         TG160                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       480        160

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-002A   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-161         TG161                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  161

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0029   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-162         TG162                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED       480        162

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0028   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-163         TG163                               FLT   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  163

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0027   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-164         TG164                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  164

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0026   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-165         TG165                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                  165

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0025   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-166         TG166                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  166

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0024   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-167         TG167                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED       481        167

                  DAMRCR  CLTGINST  CCCHCMD
                            0       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0023   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-168         TG168                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED       481        168

                  DAMRCR  CLTGINST  CCCHCMD
                            1       NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0022   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-169         TG169                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  FASTREC  1       POOL   FIXED                  169

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0021   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-170         TG170                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  MG12R13A19V1                                SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  170

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0020   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1811        D055_1003_0911                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1811

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-001F   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1812        B086_1005_1114                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0708R039E                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1812

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-001E   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1813        B246_1003_0509                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1813

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-001D   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1821        D065_1001_1009                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1821

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-001C   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1822        B374_1003_0704                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1822

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-001B   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1823        B154_1003_1217                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1823

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-001A   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1831        D033_1001_1009                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1831

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0019   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1832        B390_1005_1111                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1832

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0018   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1833        B243_1005_1014                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1833

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0017   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1841        D052_1003_0716                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1841

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0016   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1842        B504_1005_1213                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1842

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0015   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1843        B247_1003_1212                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1843

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0014   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1871        D089_1005_1209                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1871

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0013   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1872        D154_1005_1209                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1872

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0012   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1873        B420_1005_1011                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1873

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0011   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1881        D145_1003_0716                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1881

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0010   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1882        D146_1003_0716                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B1310R073F                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1882

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-000F   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1883        B281_1003_0510                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1883

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-000E   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1891        B249_1005_1011                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1891

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-000D   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1892        B228_1005_1010                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1892

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-000C   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1901        B072_1005_0907                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1901

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-000B   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1902        B111_1003_1108                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1902

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-000A   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1911        B330_1003_0505                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1911

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0009   NORMAL                     1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-1912        B320_1003_0505                      HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                  B0710R043D                                  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  1       POOL   FIXED                 1912

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7   100    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0008   NORMAL                     1
END

'''

    test1 = '''


command2;
PRINTOUT MAIN HEADER2 

PARAMETER1            PARAMETER2
        VAL11 VAL12                 VAL2

END

COMMAND1;

PRINTOUT MAIN HEADER 1

NONE

END


CMD3;
ORDERED
PRINTOUT MAIN HEADER 3

SECTION1

PARAMETER31            PARAMETER322
        VAL11 VAL12                 VAL2

END


'''

    dbtspRPSRPBSPOS = '''DBTSP:TAB=RPSRPBSPOS;
DATABASE TABLE

BLOCK   TAB             TABLE                           WRAPPED
RPADM   RPSRPBSPOS                                      NO

RPADDR     BRNO MAGNO SLOTNO INDNO BUSCONN UPD
       181    0     2      5     6 NO      ARD
       180    0     2      7     6 NO      ARD
       179    0     2      3     6 NO      ARD
       178    0     2      2     6 NO      ARD
       177    0     2     19     6 NO      ARD
       176    0     2     17     6 NO      ARD
       175    0     2     16     6 NO      ARD
       174    0     2     15     6 NO      ARD
       173    0     1     21     6 NO      ARD
       172    0     1     22     6 NO      ARD
       171    0     1     20     6 NO      ARD
       170    0     1     23     6 NO      ARD
       169    0     1     17     6 NO      ARD
       168    0     1     16     6 NO      ARD
       167    0     1     14     6 NO      ARD
       166    0     1     11     6 NO      ARD
       165    0     1     10     6 NO      ARD
       164    0     1      4     6 NO      ARD
       163    0     1      2     6 NO      ARD
       162    0     2      4     5 NO      ARD
       161    0     2      5     5 NO      ARD
       160    0     2      7     5 NO      ARD
       159    0     2      3     5 NO      ARD
       158    0     2      2     5 NO      ARD
       157    0     2     19     5 NO      ARD
       156    0     2     17     5 NO      ARD
       155    0     2     16     5 NO      ARD
       154    0     2     15     5 NO      ARD
       153    0     1     21     5 NO      ARD
       152    0     1     22     5 NO      ARD
       151    0     1     20     5 NO      ARD
       150    0     1     23     5 NO      ARD
       149    0     1     17     5 NO      ARD
       148    0     1     16     5 NO      ARD
       147    0     1     14     5 NO      ARD
       146    0     1     11     5 NO      ARD
       145    0     1     10     5 NO      ARD
       144    0     1      4     5 NO      ARD
       143    0     1      2     5 NO      ARD
       142    0     2      4     4 NO      ARD
       141    0     2      5     4 NO      ARD
       140    0     2      7     4 NO      ARD
       139    0     2      3     4 NO      ARD
       138    0     2      2     4 NO      ARD
       137    0     2     19     4 NO      ARD
       136    0     2     17     4 NO      ARD
       135    0     2     16     4 NO      ARD
       134    0     2     15     4 NO      ARD
       133    0     1     21     4 NO      ARD
       132    0     1     22     4 NO      ARD
       131    0     1     20     4 NO      ARD
       130    0     1     23     4 NO      ARD
       129    0     1     17     4 NO      ARD
       128    0     1     16     4 NO      ARD
       127    0     1     14     4 NO      ARD
       126    0     1     11     4 NO      ARD
       125    0     1     10     4 NO      ARD
       124    0     1      4     4 NO      ARD
       123    0     1      2     4 NO      ARD
       122    0     2      4     3 NO      ARD
       121    0     2      5     3 NO      ARD
       120    0     2      7     3 NO      ARD
       119    0     2      3     3 NO      ARD
       118    0     2      2     3 NO      ARD
       117    0     2     19     3 NO      ARD
       116    0     2     17     3 NO      ARD
       115    0     2     16     3 NO      ARD
       114    0     2     15     3 NO      ARD
       113    0     1     21     3 NO      ARD
       112    0     1     22     3 NO      ARD
       111    0     1     20     3 NO      ARD
       110    0     1     23     3 NO      ARD
       109    0     1     17     3 NO      ARD
       108    0     1     16     3 NO      ARD
       107    0     1     14     3 NO      ARD
       106    0     1     11     3 NO      ARD
       105    0     1     10     3 NO      ARD
       104    0     1      4     3 NO      ARD
       103    0     1      2     3 NO      ARD
       102    0     2      4     2 NO      ARD
       101    0     2      5     2 NO      ARD
       100    0     2      7     2 NO      ARD
        99    0     2      3     2 NO      ARD
        98    0     2      2     2 NO      ARD
        83    0     2     18     0 NO      CMD
        82    0     2      6     0 NO      CMD
        81    0     1     15     0 NO      CMD
        80    0     1      3     0 NO      CMD
        35    0     2     19     2 NO      ARD
        34    0     2     17     2 NO      ARD
        33    0     2     16     2 NO      ARD
        32    0     2     15     2 NO      ARD
        31    0     1     21     2 NO      ARD
        30    0     1     22     2 NO      ARD
        29    0     1     20     2 NO      ARD
        28    0     1     23     2 NO      ARD
        27    0     1     17     2 NO      ARD
        26    0     1     16     2 NO      ARD
        25    0     1     14     2 NO      ARD
        24    0     1     11     2 NO      ARD
        23    0     1     10     2 NO      ARD
        22    0     1      4     2 NO      ARD
        21    0     1      2     2 NO      ARD
        20    0     2      4     1 NO      ARD
        19    0     2      5     1 NO      ARD
        18    0     2      7     1 NO      ARD
        17    0     2      3     1 NO      ARD
        16    0     2      2     1 NO      ARD
        15    0     2     19     1 NO      ARD
        14    0     2     17     1 NO      ARD
        13    0     2     16     1 NO      ARD
        12    0     2     15     1 NO      ARD
        11    0     1     21     1 NO      ARD
        10    0     1     22     1 NO      ARD
         9    0     1     20     1 NO      ARD
         8    0     1     23     1 NO      ARD
         7    0     1     17     1 NO      ARD
         6    0     1     16     1 NO      ARD
         5    0     1     14     1 NO      ARD
         4    0     1     11     1 NO      ARD
         3    0     1     10     1 NO      ARD
         2    0     1      4     1 NO      ARD
         1    0     1      2     1 NO      ARD

END
'''

    ntcopEvo8200 = '''
NTCOP:SNT=All;
SWITCHING NETWORK TERMINAL CONNECTION DATA

SNT           SNTV  SDIP        DIP     DEV                       SNTINL
ETM4-0            1 0SDIPM4     00SDI   ETM4-0&&-31                 0
                                10SDI   ETM4-32&&-63                1
                                20SDI   ETM4-64&&-95                2
                                30SDI   ETM4-96&&-127               3
                                40SDI   ETM4-128&&-159              4
                                50SDI   ETM4-160&&-191              5
                                60SDI   ETM4-192&&-223              6
                                70SDI   ETM4-224&&-255              7
                                80SDI   ETM4-256&&-287              8
                                90SDI   ETM4-288&&-319              9
                                100SDI  ETM4-320&&-351             10
                                110SDI  ETM4-352&&-383             11
                                120SDI  ETM4-384&&-415             12
                                130SDI  ETM4-416&&-447             13
                                140SDI  ETM4-448&&-479             14
                                150SDI  ETM4-480&&-511             15
                                160SDI  ETM4-512&&-543             16
                                170SDI  ETM4-544&&-575             17
                                180SDI  ETM4-576&&-607             18
                                190SDI  ETM4-608&&-639             19
                                200SDI  ETM4-640&&-671             20
                                210SDI  ETM4-672&&-703             21
                                220SDI  ETM4-704&&-735             22
                                230SDI  ETM4-736&&-767             23
                                240SDI  ETM4-768&&-799             24
                                250SDI  ETM4-800&&-831             25
                                260SDI  ETM4-832&&-863             26
                                270SDI  ETM4-864&&-895             27
                                280SDI  ETM4-896&&-927             28
                                290SDI  ETM4-928&&-959             29
                                300SDI  ETM4-960&&-991             30
                                310SDI  ETM4-992&&-1023            31
                                320SDI  ETM4-1024&&-1055           32
                                330SDI  ETM4-1056&&-1087           33
                                340SDI  ETM4-1088&&-1119           34
                                350SDI  ETM4-1120&&-1151           35
                                360SDI  ETM4-1152&&-1183           36
                                370SDI  ETM4-1184&&-1215           37
                                380SDI  ETM4-1216&&-1247           38
                                390SDI  ETM4-1248&&-1279           39
                                400SDI  ETM4-1280&&-1311           40
                                410SDI  ETM4-1312&&-1343           41
                                420SDI  ETM4-1344&&-1375           42
                                430SDI  ETM4-1376&&-1407           43
                                440SDI  ETM4-1408&&-1439           44
                                450SDI  ETM4-1440&&-1471           45
                                460SDI  ETM4-1472&&-1503           46
                                470SDI  ETM4-1504&&-1535           47
                                480SDI  ETM4-1536&&-1567           48
                                490SDI  ETM4-1568&&-1599           49
                                500SDI  ETM4-1600&&-1631           50
                                510SDI  ETM4-1632&&-1663           51
                                520SDI  ETM4-1664&&-1695           52
                                530SDI  ETM4-1696&&-1727           53
                                540SDI  ETM4-1728&&-1759           54
                                550SDI  ETM4-1760&&-1791           55
                                560SDI  ETM4-1792&&-1823           56
                                570SDI  ETM4-1824&&-1855           57
                                580SDI  ETM4-1856&&-1887           58
                                590SDI  ETM4-1888&&-1919           59
                                600SDI  ETM4-1920&&-1951           60
                                610SDI  ETM4-1952&&-1983           61
                                620SDI  ETM4-1984&&-2015           62
                    1SDIPM4     01SDI   ETM4-2016&&-2047           63
                                11SDI   ETM4-2048&&-2079           64
                                21SDI   ETM4-2080&&-2111           65
                                31SDI   ETM4-2112&&-2143           66
                                41SDI   ETM4-2144&&-2175           67
                                51SDI   ETM4-2176&&-2207           68
                                61SDI   ETM4-2208&&-2239           69
                                71SDI   ETM4-2240&&-2271           70
                                81SDI   ETM4-2272&&-2303           71
                                91SDI   ETM4-2304&&-2335           72
                                101SDI  ETM4-2336&&-2367           73
                                111SDI  ETM4-2368&&-2399           74
                                121SDI  ETM4-2400&&-2431           75
                                131SDI  ETM4-2432&&-2463           76
                                141SDI  ETM4-2464&&-2495           77
                                151SDI  ETM4-2496&&-2527           78
                                161SDI  ETM4-2528&&-2559           79
                                171SDI  ETM4-2560&&-2591           80
                                181SDI  ETM4-2592&&-2623           81
                                191SDI  ETM4-2624&&-2655           82
                                201SDI  ETM4-2656&&-2687           83
                                211SDI  ETM4-2688&&-2719           84
                                221SDI  ETM4-2720&&-2751           85
                                231SDI  ETM4-2752&&-2783           86
                                241SDI  ETM4-2784&&-2815           87
                                251SDI  ETM4-2816&&-2847           88
                                261SDI  ETM4-2848&&-2879           89
                                271SDI  ETM4-2880&&-2911           90
                                281SDI  ETM4-2912&&-2943           91
                                291SDI  ETM4-2944&&-2975           92
                                301SDI  ETM4-2976&&-3007           93
                                311SDI  ETM4-3008&&-3039           94
                                321SDI  ETM4-3040&&-3071           95
                                331SDI  ETM4-3072&&-3103           96
                                341SDI  ETM4-3104&&-3135           97
                                351SDI  ETM4-3136&&-3167           98
                                361SDI  ETM4-3168&&-3199           99
                                371SDI  ETM4-3200&&-3231          100
                                381SDI  ETM4-3232&&-3263          101
                                391SDI  ETM4-3264&&-3295          102
                                401SDI  ETM4-3296&&-3327          103
                                411SDI  ETM4-3328&&-3359          104
                                421SDI  ETM4-3360&&-3391          105
                                431SDI  ETM4-3392&&-3423          106
                                441SDI  ETM4-3424&&-3455          107
                                451SDI  ETM4-3456&&-3487          108
                                461SDI  ETM4-3488&&-3519          109
                                471SDI  ETM4-3520&&-3551          110
                                481SDI  ETM4-3552&&-3583          111
                                491SDI  ETM4-3584&&-3615          112
                                501SDI  ETM4-3616&&-3647          113
                                511SDI  ETM4-3648&&-3679          114
                                521SDI  ETM4-3680&&-3711          115
                                531SDI  ETM4-3712&&-3743          116
                                541SDI  ETM4-3744&&-3775          117
                                551SDI  ETM4-3776&&-3807          118
                                561SDI  ETM4-3808&&-3839          119
                                571SDI  ETM4-3840&&-3871          120
                                581SDI  ETM4-3872&&-3903          121
                                591SDI  ETM4-3904&&-3935          122
                                601SDI  ETM4-3936&&-3967          123
                                611SDI  ETM4-3968&&-3999          124
                                621SDI  ETM4-4000&&-4031          125
                    2SDIPM4     02SDI   ETM4-4032&&-4063          126
                                12SDI   ETM4-4064&&-4095          127
                                22SDI   ETM4-4096&&-4127          128
                                32SDI   ETM4-4128&&-4159          129
                                42SDI   ETM4-4160&&-4191          130
                                52SDI   ETM4-4192&&-4223          131
                                62SDI   ETM4-4224&&-4255          132
                                72SDI   ETM4-4256&&-4287          133
                                82SDI   ETM4-4288&&-4319          134
                                92SDI   ETM4-4320&&-4351          135
                                102SDI  ETM4-4352&&-4383          136
                                112SDI  ETM4-4384&&-4415          137
                                122SDI  ETM4-4416&&-4447          138
                                132SDI  ETM4-4448&&-4479          139
                                142SDI  ETM4-4480&&-4511          140
                                152SDI  ETM4-4512&&-4543          141
                                162SDI  ETM4-4544&&-4575          142
                                172SDI  ETM4-4576&&-4607          143
                                182SDI  ETM4-4608&&-4639          144
                                192SDI  ETM4-4640&&-4671          145
                                202SDI  ETM4-4672&&-4703          146
                                212SDI  ETM4-4704&&-4735          147
                                222SDI  ETM4-4736&&-4767          148
                                232SDI  ETM4-4768&&-4799          149
                                242SDI  ETM4-4800&&-4831          150
                                252SDI  ETM4-4832&&-4863          151
                                262SDI  ETM4-4864&&-4895          152
                                272SDI  ETM4-4896&&-4927          153
                                282SDI  ETM4-4928&&-4959          154
                                292SDI  ETM4-4960&&-4991          155
                                302SDI  ETM4-4992&&-5023          156
                                312SDI  ETM4-5024&&-5055          157
                                322SDI  ETM4-5056&&-5087          158
                                332SDI  ETM4-5088&&-5119          159
                                342SDI  ETM4-5120&&-5151          160
                                352SDI  ETM4-5152&&-5183          161
                                362SDI  ETM4-5184&&-5215          162
                                372SDI  ETM4-5216&&-5247          163
                                382SDI  ETM4-5248&&-5279          164
                                392SDI  ETM4-5280&&-5311          165
                                402SDI  ETM4-5312&&-5343          166
                                412SDI  ETM4-5344&&-5375          167
                                422SDI  ETM4-5376&&-5407          168
                                432SDI  ETM4-5408&&-5439          169
                                442SDI  ETM4-5440&&-5471          170
                                452SDI  ETM4-5472&&-5503          171
                                462SDI  ETM4-5504&&-5535          172
                                472SDI  ETM4-5536&&-5567          173
                                482SDI  ETM4-5568&&-5599          174
                                492SDI  ETM4-5600&&-5631          175
                                502SDI  ETM4-5632&&-5663          176
                                512SDI  ETM4-5664&&-5695          177
                                522SDI  ETM4-5696&&-5727          178
                                532SDI  ETM4-5728&&-5759          179
                                542SDI  ETM4-5760&&-5791          180
                                552SDI  ETM4-5792&&-5823          181
                                562SDI  ETM4-5824&&-5855          182
                                572SDI  ETM4-5856&&-5887          183
                                582SDI  ETM4-5888&&-5919          184
                                592SDI  ETM4-5920&&-5951          185
                                602SDI  ETM4-5952&&-5983          186
                                612SDI  ETM4-5984&&-6015          187
                                622SDI  ETM4-6016&&-6047          188
                    3SDIPM4     03SDI   ETM4-6048&&-6079          189
                                13SDI   ETM4-6080&&-6111          190
                                23SDI   ETM4-6112&&-6143          191
                                33SDI   ETM4-6144&&-6175          192
                                43SDI   ETM4-6176&&-6207          193
                                53SDI   ETM4-6208&&-6239          194
                                63SDI   ETM4-6240&&-6271          195
                                73SDI   ETM4-6272&&-6303          196
                                83SDI   ETM4-6304&&-6335          197
                                93SDI   ETM4-6336&&-6367          198
                                103SDI  ETM4-6368&&-6399          199
                                113SDI  ETM4-6400&&-6431          200
                                123SDI  ETM4-6432&&-6463          201
                                133SDI  ETM4-6464&&-6495          202
                                143SDI  ETM4-6496&&-6527          203
                                153SDI  ETM4-6528&&-6559          204
                                163SDI  ETM4-6560&&-6591          205
                                173SDI  ETM4-6592&&-6623          206
                                183SDI  ETM4-6624&&-6655          207
                                193SDI  ETM4-6656&&-6687          208
                                203SDI  ETM4-6688&&-6719          209
                                213SDI  ETM4-6720&&-6751          210
                                223SDI  ETM4-6752&&-6783          211
                                233SDI  ETM4-6784&&-6815          212
                                243SDI  ETM4-6816&&-6847          213
                                253SDI  ETM4-6848&&-6879          214
                                263SDI  ETM4-6880&&-6911          215
                                273SDI  ETM4-6912&&-6943          216
                                283SDI  ETM4-6944&&-6975          217
                                293SDI  ETM4-6976&&-7007          218
                                303SDI  ETM4-7008&&-7039          219
                                313SDI  ETM4-7040&&-7071          220
                                323SDI  ETM4-7072&&-7103          221
                                333SDI  ETM4-7104&&-7135          222
                                343SDI  ETM4-7136&&-7167          223
                                353SDI  ETM4-7168&&-7199          224
                                363SDI  ETM4-7200&&-7231          225
                                373SDI  ETM4-7232&&-7263          226
                                383SDI  ETM4-7264&&-7295          227
                                393SDI  ETM4-7296&&-7327          228
                                403SDI  ETM4-7328&&-7359          229
                                413SDI  ETM4-7360&&-7391          230
                                423SDI  ETM4-7392&&-7423          231
                                433SDI  ETM4-7424&&-7455          232
                                443SDI  ETM4-7456&&-7487          233
                                453SDI  ETM4-7488&&-7519          234
                                463SDI  ETM4-7520&&-7551          235
                                473SDI  ETM4-7552&&-7583          236
                                483SDI  ETM4-7584&&-7615          237
                                493SDI  ETM4-7616&&-7647          238
                                503SDI  ETM4-7648&&-7679          239
                                513SDI  ETM4-7680&&-7711          240
                                523SDI  ETM4-7712&&-7743          241
                                533SDI  ETM4-7744&&-7775          242
                                543SDI  ETM4-7776&&-7807          243
                                553SDI  ETM4-7808&&-7839          244
                                563SDI  ETM4-7840&&-7871          245
                                573SDI  ETM4-7872&&-7903          246
                                583SDI  ETM4-7904&&-7935          247
                                593SDI  ETM4-7936&&-7967          248
                                603SDI  ETM4-7968&&-7999          249
                                613SDI  ETM4-8000&&-8031          250
                                623SDI  ETM4-8032&&-8063          251
                    4SDIPM4     04SDI   ETM4-8064&&-8095          252
                                14SDI   ETM4-8096&&-8127          253
                                24SDI   ETM4-8128&&-8159          254
                                34SDI   ETM4-8160&&-8191          255
                                44SDI   ETM4-8192&&-8223          256
                                54SDI   ETM4-8224&&-8255          257
                                64SDI   ETM4-8256&&-8287          258
                                74SDI   ETM4-8288&&-8319          259
                                84SDI   ETM4-8320&&-8351          260
                                94SDI   ETM4-8352&&-8383          261
                                104SDI  ETM4-8384&&-8415          262
                                114SDI  ETM4-8416&&-8447          263
                                124SDI  ETM4-8448&&-8479          264
                                134SDI  ETM4-8480&&-8511          265
                                144SDI  ETM4-8512&&-8543          266
                                154SDI  ETM4-8544&&-8575          267
                                164SDI  ETM4-8576&&-8607          268
                                174SDI  ETM4-8608&&-8639          269
                                184SDI  ETM4-8640&&-8671          270
                                194SDI  ETM4-8672&&-8703          271
                                204SDI  ETM4-8704&&-8735          272
                                214SDI  ETM4-8736&&-8767          273
                                224SDI  ETM4-8768&&-8799          274
                                234SDI  ETM4-8800&&-8831          275
                                244SDI  ETM4-8832&&-8863          276
                                254SDI  ETM4-8864&&-8895          277
                                264SDI  ETM4-8896&&-8927          278
                                274SDI  ETM4-8928&&-8959          279
                                284SDI  ETM4-8960&&-8991          280
                                294SDI  ETM4-8992&&-9023          281
                                304SDI  ETM4-9024&&-9055          282
                                314SDI  ETM4-9056&&-9087          283
                                324SDI  ETM4-9088&&-9119          284
                                334SDI  ETM4-9120&&-9151          285
                                344SDI  ETM4-9152&&-9183          286
                                354SDI  ETM4-9184&&-9215          287
                                364SDI  ETM4-9216&&-9247          288
                                374SDI  ETM4-9248&&-9279          289
                                384SDI  ETM4-9280&&-9311          290
                                394SDI  ETM4-9312&&-9343          291
                                404SDI  ETM4-9344&&-9375          292
                                414SDI  ETM4-9376&&-9407          293
                                424SDI  ETM4-9408&&-9439          294
                                434SDI  ETM4-9440&&-9471          295
                                444SDI  ETM4-9472&&-9503          296
                                454SDI  ETM4-9504&&-9535          297
                                464SDI  ETM4-9536&&-9567          298
                                474SDI  ETM4-9568&&-9599          299
                                484SDI  ETM4-9600&&-9631          300
                                494SDI  ETM4-9632&&-9663          301
                                504SDI  ETM4-9664&&-9695          302
                                514SDI  ETM4-9696&&-9727          303
                                524SDI  ETM4-9728&&-9759          304
                                534SDI  ETM4-9760&&-9791          305
                                544SDI  ETM4-9792&&-9823          306
                                554SDI  ETM4-9824&&-9855          307
                                564SDI  ETM4-9856&&-9887          308
                                574SDI  ETM4-9888&&-9919          309
                                584SDI  ETM4-9920&&-9951          310
                                594SDI  ETM4-9952&&-9983          311
                                604SDI  ETM4-9984&&-10015         312
                                614SDI  ETM4-10016&&-10047        313
                                624SDI  ETM4-10048&&-10079        314
                    5SDIPM4     05SDI   ETM4-10080&&-10111        315
                                15SDI   ETM4-10112&&-10143        316
                                25SDI   ETM4-10144&&-10175        317
                                35SDI   ETM4-10176&&-10207        318
                                45SDI   ETM4-10208&&-10239        319
                                55SDI   ETM4-10240&&-10271        320
                                65SDI   ETM4-10272&&-10303        321
                                75SDI   ETM4-10304&&-10335        322
                                85SDI   ETM4-10336&&-10367        323
                                95SDI   ETM4-10368&&-10399        324
                                105SDI  ETM4-10400&&-10431        325
                                115SDI  ETM4-10432&&-10463        326
                                125SDI  ETM4-10464&&-10495        327
                                135SDI  ETM4-10496&&-10527        328
                                145SDI  ETM4-10528&&-10559        329
                                155SDI  ETM4-10560&&-10591        330
                                165SDI  ETM4-10592&&-10623        331
                                175SDI  ETM4-10624&&-10655        332
                                185SDI  ETM4-10656&&-10687        333
                                195SDI  ETM4-10688&&-10719        334
                                205SDI  ETM4-10720&&-10751        335
                                215SDI  ETM4-10752&&-10783        336
                                225SDI  ETM4-10784&&-10815        337
                                235SDI  ETM4-10816&&-10847        338
                                245SDI  ETM4-10848&&-10879        339
                                255SDI  ETM4-10880&&-10911        340
                                265SDI  ETM4-10912&&-10943        341
                                275SDI  ETM4-10944&&-10975        342
                                285SDI  ETM4-10976&&-11007        343
                                295SDI  ETM4-11008&&-11039        344
                                305SDI  ETM4-11040&&-11071        345
                                315SDI  ETM4-11072&&-11103        346
                                325SDI  ETM4-11104&&-11135        347
                                335SDI  ETM4-11136&&-11167        348
                                345SDI  ETM4-11168&&-11199        349
                                355SDI  ETM4-11200&&-11231        350
                                365SDI  ETM4-11232&&-11263        351
                                375SDI  ETM4-11264&&-11295        352
                                385SDI  ETM4-11296&&-11327        353
                                395SDI  ETM4-11328&&-11359        354
                                405SDI  ETM4-11360&&-11391        355
                                415SDI  ETM4-11392&&-11423        356
                                425SDI  ETM4-11424&&-11455        357
                                435SDI  ETM4-11456&&-11487        358
                                445SDI  ETM4-11488&&-11519        359
                                455SDI  ETM4-11520&&-11551        360
                                465SDI  ETM4-11552&&-11583        361
                                475SDI  ETM4-11584&&-11615        362
                                485SDI  ETM4-11616&&-11647        363
                                495SDI  ETM4-11648&&-11679        364
                                505SDI  ETM4-11680&&-11711        365
                                515SDI  ETM4-11712&&-11743        366
                                525SDI  ETM4-11744&&-11775        367
                                535SDI  ETM4-11776&&-11807        368
                                545SDI  ETM4-11808&&-11839        369
                                555SDI  ETM4-11840&&-11871        370
                                565SDI  ETM4-11872&&-11903        371
                                575SDI  ETM4-11904&&-11935        372
                                585SDI  ETM4-11936&&-11967        373
                                595SDI  ETM4-11968&&-11999        374
                                605SDI  ETM4-12000&&-12031        375
                                615SDI  ETM4-12032&&-12063        376
                                625SDI  ETM4-12064&&-12095        377
                    6SDIPM4     06SDI   ETM4-12096&&-12127        378
                                16SDI   ETM4-12128&&-12159        379
                                26SDI   ETM4-12160&&-12191        380
                                36SDI   ETM4-12192&&-12223        381
                                46SDI   ETM4-12224&&-12255        382
                                56SDI   ETM4-12256&&-12287        383
                                66SDI   ETM4-12288&&-12319        384
                                76SDI   ETM4-12320&&-12351        385
                                86SDI   ETM4-12352&&-12383        386
                                96SDI   ETM4-12384&&-12415        387
                                106SDI  ETM4-12416&&-12447        388
                                116SDI  ETM4-12448&&-12479        389
                                126SDI  ETM4-12480&&-12511        390
                                136SDI  ETM4-12512&&-12543        391
                                146SDI  ETM4-12544&&-12575        392
                                156SDI  ETM4-12576&&-12607        393
                                166SDI  ETM4-12608&&-12639        394
                                176SDI  ETM4-12640&&-12671        395
                                186SDI  ETM4-12672&&-12703        396
                                196SDI  ETM4-12704&&-12735        397
                                206SDI  ETM4-12736&&-12767        398
                                216SDI  ETM4-12768&&-12799        399
                                226SDI  ETM4-12800&&-12831        400
                                236SDI  ETM4-12832&&-12863        401
                                246SDI  ETM4-12864&&-12895        402
                                256SDI  ETM4-12896&&-12927        403
                                266SDI  ETM4-12928&&-12959        404
                                276SDI  ETM4-12960&&-12991        405
                                286SDI  ETM4-12992&&-13023        406
                                296SDI  ETM4-13024&&-13055        407
                                306SDI  ETM4-13056&&-13087        408
                                316SDI  ETM4-13088&&-13119        409
                                326SDI  ETM4-13120&&-13151        410
                                336SDI  ETM4-13152&&-13183        411
                                346SDI  ETM4-13184&&-13215        412
                                356SDI  ETM4-13216&&-13247        413
                                366SDI  ETM4-13248&&-13279        414
                                376SDI  ETM4-13280&&-13311        415
                                386SDI  ETM4-13312&&-13343        416
                                396SDI  ETM4-13344&&-13375        417
                                406SDI  ETM4-13376&&-13407        418
                                416SDI  ETM4-13408&&-13439        419
                                426SDI  ETM4-13440&&-13471        420
                                436SDI  ETM4-13472&&-13503        421
                                446SDI  ETM4-13504&&-13535        422
                                456SDI  ETM4-13536&&-13567        423
                                466SDI  ETM4-13568&&-13599        424
                                476SDI  ETM4-13600&&-13631        425
                                486SDI  ETM4-13632&&-13663        426
                                496SDI  ETM4-13664&&-13695        427
                                506SDI  ETM4-13696&&-13727        428
                                516SDI  ETM4-13728&&-13759        429
                                526SDI  ETM4-13760&&-13791        430
                                536SDI  ETM4-13792&&-13823        431
                                546SDI  ETM4-13824&&-13855        432
                                556SDI  ETM4-13856&&-13887        433
                                566SDI  ETM4-13888&&-13919        434
                                576SDI  ETM4-13920&&-13951        435
                                586SDI  ETM4-13952&&-13983        436
                                596SDI  ETM4-13984&&-14015        437
                                606SDI  ETM4-14016&&-14047        438
                                616SDI  ETM4-14048&&-14079        439
                                626SDI  ETM4-14080&&-14111        440
                    7SDIPM4     07SDI   ETM4-14112&&-14143        441
                                17SDI   ETM4-14144&&-14175        442
                                27SDI   ETM4-14176&&-14207        443
                                37SDI   ETM4-14208&&-14239        444
                                47SDI   ETM4-14240&&-14271        445
                                57SDI   ETM4-14272&&-14303        446
                                67SDI   ETM4-14304&&-14335        447
                                77SDI   ETM4-14336&&-14367        448
                                87SDI   ETM4-14368&&-14399        449
                                97SDI   ETM4-14400&&-14431        450
                                107SDI  ETM4-14432&&-14463        451
                                117SDI  ETM4-14464&&-14495        452
                                127SDI  ETM4-14496&&-14527        453
                                137SDI  ETM4-14528&&-14559        454
                                147SDI  ETM4-14560&&-14591        455
                                157SDI  ETM4-14592&&-14623        456
                                167SDI  ETM4-14624&&-14655        457
                                177SDI  ETM4-14656&&-14687        458
                                187SDI  ETM4-14688&&-14719        459
                                197SDI  ETM4-14720&&-14751        460
                                207SDI  ETM4-14752&&-14783        461
                                217SDI  ETM4-14784&&-14815        462
                                227SDI  ETM4-14816&&-14847        463
                                237SDI  ETM4-14848&&-14879        464
                                247SDI  ETM4-14880&&-14911        465
                                257SDI  ETM4-14912&&-14943        466
                                267SDI  ETM4-14944&&-14975        467
                                277SDI  ETM4-14976&&-15007        468
                                287SDI  ETM4-15008&&-15039        469
                                297SDI  ETM4-15040&&-15071        470
                                307SDI  ETM4-15072&&-15103        471
                                317SDI  ETM4-15104&&-15135        472
                                327SDI  ETM4-15136&&-15167        473
                                337SDI  ETM4-15168&&-15199        474
                                347SDI  ETM4-15200&&-15231        475
                                357SDI  ETM4-15232&&-15263        476
                                367SDI  ETM4-15264&&-15295        477
                                377SDI  ETM4-15296&&-15327        478
                                387SDI  ETM4-15328&&-15359        479
                                397SDI  ETM4-15360&&-15391        480
                                407SDI  ETM4-15392&&-15423        481
                                417SDI  ETM4-15424&&-15455        482
                                427SDI  ETM4-15456&&-15487        483
                                437SDI  ETM4-15488&&-15519        484
                                447SDI  ETM4-15520&&-15551        485
                                457SDI  ETM4-15552&&-15583        486
                                467SDI  ETM4-15584&&-15615        487
                                477SDI  ETM4-15616&&-15647        488
                                487SDI  ETM4-15648&&-15679        489
                                497SDI  ETM4-15680&&-15711        490
                                507SDI  ETM4-15712&&-15743        491
                                517SDI  ETM4-15744&&-15775        492
                                527SDI  ETM4-15776&&-15807        493
                                537SDI  ETM4-15808&&-15839        494
                                547SDI  ETM4-15840&&-15871        495
                                557SDI  ETM4-15872&&-15903        496
                                567SDI  ETM4-15904&&-15935        497
                                577SDI  ETM4-15936&&-15967        498
                                587SDI  ETM4-15968&&-15999        499
                                597SDI  ETM4-16000&&-16031        500
                                607SDI  ETM4-16032&&-16063        501
                                617SDI  ETM4-16064&&-16095        502
                                627SDI  ETM4-16096&&-16127        503

SNT           PROT   SDIP    SUBSNT DEFPST
ETM4-0        0      0SDIPM4 0
                     1SDIPM4
                     2SDIPM4
                     3SDIPM4
                     4SDIPM4
                     5SDIPM4
                     6SDIPM4
                     7SDIPM4
END

'''


    c7sdpAll = '''C7DSP:ENUM=ALL;
CCITT7 DISTURBANCE SUPERVISION DATA

ENUM STATE  DST  DELAY  ACL
   0 INIT     1    180  A3
   1 INIT     7    181  A2
   2 INIT     1    182  A3
   3 INIT     6    180  A1
   4 DEF      1    180  A3
   5 INIT     4    185  A3
   6 INIT     3    180  A3
   7 NOTDEF
   8 INIT     2    187  A3
END'''

    test3Level = '''
dummycmd;
dummyheader

ID1 PAR11 PAR12 SUB2 SUBPAR21 SUB22 SUBPARA221 SUBPARA222
1   P1    P2 P3 S1   SP21     S2A   SP221, I   SP222
                     SP22     S2B   SP22A      SPBB
                S2   V1       SSA   AAA        BBB
                                    fff         g
                              V2    shi+       f4ck
                S3            S111  GGG
2   P12A  PPP   S4   VAA
END
'''

    ihrsp = '''IHRSP;
ROUTER SUPERVISION DATA

SVRATE      SVTO          SVMAXTX       SVMINRX
10          3             2             2

SVI         SVR
65          82


VIFP                 IPMIGR    HOFF     TTL
ETH-51               YES       5        1

IP              NETMASK             HOME     NOW
10.77.135.180   255.255.255.240     ETHA     ATHOME
10.77.135.181   255.255.255.240     ETHB     ATHOME

PINGA           PINGB
10.77.135.189   10.77.135.190

GW                                      STATE
10.77.135.177                           WO
10.77.135.178                           WO

VIFP                 IPMIGR    HOFF     TTL
ETH-55               YES       5        1

IP              NETMASK             HOME     NOW
50.77.135.180   255.255.255.240     ETHA     ATHOME
50.77.135.181   255.255.255.240     ETHB     ATHOME

PINGA           PINGB
50.77.135.189   50.77.135.190

GW                                      STATE
50.77.135.177                           WO
50.77.135.178                           WO

END

'''


    rfsdp = '''
rfsdp:tableid=0,spid=all;
SUBSCRIBER PROFILE ID DATA

TABLEID
      0

SPID     ACTION    GPRIO  FDDARFCN  WPRIO  EARFCN  LPRIO
   1     DEFPRIO       0         0      1
   2     DEFPRIO       7     16383      2
 100     DEFPRIO       1                        0      3
 101     DEFPRIO       6                    65535      4
 255     NOACTION
 256     DELPRIO
DEFAULT  NOACTION

END
'''

    rlbdpAll = '''

RLBDP:cell=all;
CELL CONFIGURATION BPC DATA

CELL
174320A

CHGR   NUMREQBPC  NUMREQEGPRSBPC  NUMREQCS3CS4BPC  TN7BCCH  EACPREF
 0       8          0               0              GPRS     YES

       ETCHTN           TNBCCH  NUMREQE2ABPC
       0 1 2 3 4 5 6 7  GPRS      0

CHGR   NUMREQBPC  NUMREQEGPRSBPC  NUMREQCS3CS4BPC  TN7BCCH  EACPREF
 1      24         12               0

       ETCHTN           TNBCCH  NUMREQE2ABPC
       0 1 2 3 4 5 6 7            8


CELL
174330A

CHGR   NUMREQBPC  NUMREQEGPRSBPC  NUMREQCS3CS4BPC  TN7BCCH  EACPREF
 0       8          0               0              GPRS     YES

       ETCHTN           TNBCCH  NUMREQE2ABPC
       0 1 2 3 4 5 6 7  GPRS      0

CHGR   NUMREQBPC  NUMREQEGPRSBPC  NUMREQCS3CS4BPC  TN7BCCH  EACPREF
 1      56         28               0

       ETCHTN           TNBCCH  NUMREQE2ABPC
       0 1 2 3 4 5 6 7            0


END

'''

    dbtsp1 = '''dbtsp:tab=axepars,setname=cme20bscf;
DATABASE TABLE

BLOCK   TAB             TABLE                           WRAPPED
PARA    AXEPARS                                         YES

NAME            SETNAME         PARID      VALUE UNIT CLASS   DISTRIB
MULTICCCH       CME20BSCF             8174     1      aaATURE IMMdD

                                STATUS  FCVSET FCVALUE DCINFO FCODE
                                UPDATED FALSE        1 UNDEF     10

NAME            SETNAME         PARID      VALUE UNIT CLASS   DISTRIB
MULTIBANDCELL   CME20BSCF          5558173     1      FEATURE IMMgD

                                STATUS  FCVSET FCVALUE DCINFO FCODE
                                UPDATED FALSE        1 UNDEF    330

NAME            SETNAME         PARID      VALUE UNIT CLASS   DISTRIB
AOIP            CME20BSCF             7117 65535      FEATtRE IMMhD

                                STATUS  FCVSET FCVALUE DCINFO FCODE
                                UPDATED FAffE    65535 UNDyF    550

END
'''

    dbtsp2 = '''dbtsp:TAB=axepars;
DATABASE TABLE

BLOCK   TAB             TABLE                           WRAPPED
PARA    AXEPARS                                         YES

NAME            SETNAME         PARID      VALUE UNIT CLASS   DISTRIB
XMSYSMODE       SDAF                  8191     0      FEATURE IMMED

                                STATUS  FCVSET FCVALUE DCINFO FCODE
                                LOADED  FALSE        0 UNDEF      0

NAME            SETNAME         PARID      VALUE UNIT CLASS   DISTRIB
UPUCAUSE0       MTPC                  8190     0      CUSTOM  IMMED

                                STATUS  FCVSET FCVALUE DCINFO FCODE
                                UPDATED FALSE        0 UNDEF      0

NAME            SETNAME         PARID      VALUE UNIT CLASS   DISTRIB
UPUSUPPRESS     MTPC                  8189     1      CUSTOM  IMMED

                                STATUS  FCVSET FCVALUE DCINFO FCODE
                                UPDATED FALSE        1 UNDEF      0

END'''


    rlmfpAll = '''
rlmfp:CELL=ALL;
       
CELL MEASUREMENT FREQUENCIES

CELL
1361C1

LISTTYPE
IDLE

MBCCHNO
  15   27   39   51   63  515  527  539  551  563  575  587  599

LISTTYPE
ACTIVE

MBCCHNO
  AA   BB   CC   DD   EE  FFF  GGG  HHH  III  JJJ  KKK  LLL  MMM  DDD

TEST MEASUREMENT FREQUENCIES

MBCCHNO

END

'''

    rxmopTgs = '''
rxmop;
bla

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-210         TG210                               HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                                 MG12R13A25V0   MG12R13A25V0  SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  210

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                   7    20    1     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0009   NORMAL        1510         1

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-500         B415_1003_0514                      HYB   BB    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                                 B0711R045G     B0711R045G    SCM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  NODEL    1       POOL   FIXED                  500

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA
                  10    20    0     20

                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0008   NORMAL        1510         1
END


'''

    rllopAll = '''
PRINTOUT

CELL     DBPSTATE  DBPBCCHSTATE
1361C1   ACTIVE    ACTIVE

SCTYPE   SSDESDL  QDESDL  LCOMPDL  QCOMPDL
UL        90      30        5       55

         BSPWRMINP  BSPWRMINN
                    20

SCTYPE   SSDESDL  QDESDL  LCOMPDL  QCOMPDL
OL        90      30        5       55

         BSPWRMINP  BSPWRMINN
                    20
END
'''

    exrup = '''
MAIN HEADER

RP    TYPE     TWIN
   0  RPSCB1E

SUNAME        SUID                              SUPTR  CM  EM
RPFDR         9000/CXC 146 10        R1B01          1  31
RPMMR         9000/CXC 146 20        R2B01         86  30
RPMBHR        9000/CXC 146 21        R6A06        104  29
RPIFDR        9000/CXC 146 23        R1A01         66  28
INETR         9000/CXC 146 151       R1C01        125  27
SCBSNMPR      9000/CXC 146 143       R3A04         67  26
SCBSWMGR      9000/CXC 146 145       R2F01        138  25
RIEXR         9000/CXC 146 097       R6G01        126  16


'''

    rxmop = '''
MAIN HEADER

MO                RSITE                               COMB  FHOP  MODEL
RXOTG-21          TG21                                HYB   SY    G12

                  SWVERREPL      SWVERDLD       SWVERACT      TMODE
                                 MG12R13A25V0   MG12R13A25V0  TDM

                  CONFMD  CONFACT  TRACO  ABISALLOC  CLUSTERID  SCGR
                  MINDIST  3       POOL   FIXED

                  DAMRCR  CLTGINST  CCCHCMD
                                    NORMAL

                  PTA  JBSDL  PAL  JBPTA


                  TGFID         SIGDEL        BSSWANTED    PACKALG
                  H'0000-0046   NORMAL        1611


'''

    rlsrpAll = '''rlsrp:cell=all;
CELL SYSTEM INFORMATION RAT PRIORITY DATA

CELL     PRIOCR  BCAST    FREE  REQ
112C202  OFF

RATPRIO  MEASTHR  PRIOTHR  HPRIO  TRES
         15        0       0      0

FDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU

EARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINE

TDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU


CELL     PRIOCR  BCAST    FREE  REQ
071C169  ON      NO        0    NA

RATPRIO  MEASTHR  PRIOTHR  HPRIO  TRES
1        15        0       0      0

EARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINE
1575    7        22        22         0
3013    5        22        22         0

TDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU

FDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU
3013               9         9         0

CELL     PRIOCR  BCAST    FREE  REQ
042C144  OFF

RATPRIO  MEASTHR  PRIOTHR  HPRIO  TRES
         15        0       0      0

FDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU

EARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINE

TDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU

END'''

    testStoreAsListofLists = '''
printout name

CELL CELLPAR1 CHGR CHGRPAR1
C1   CP1         0 CGP1

              CHGRP2
              CGP2

              CHGR CHGRPAR1
                 1 CGP2

              CHGRP2


CELL CELLPAR1 CHGR CHGRPAR1
C2   CP1
                 
'''
    
    rlumpAll = '''
rlump:cell=all;
CELL UTRAN MEASUREMENT FREQUENCY DATA

CELL
112C202

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
111C201

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
092C188

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
091C187

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
092C186

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
091C185

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
082C180

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
082C179

LISTTYPE
IDLE

     UMFI
     3010-131-NODIV

LISTTYPE
ACTIVE

     UMFI
     3010-131-NODIV

CELL
082C178

LISTTYPE
IDLE

     UMFI
     3010-131-NODIV

LISTTYPE
ACTIVE

     UMFI
     3010-131-NODIV

CELL
081C177

LISTTYPE
IDLE

     UMFI
     3010-131-NODIV

LISTTYPE
ACTIVE

     UMFI
     3010-131-NODIV

CELL
072C172

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
072C171

LISTTYPE
IDLE

     UMFI
     3013-391-NODIV

LISTTYPE
ACTIVE

     UMFI
     3013-391-NODIV

CELL
072C170

LISTTYPE
IDLE

     UMFI
     3013-391-NODIV

LISTTYPE
ACTIVE

     UMFI
     3013-391-NODIV

CELL
071C169

LISTTYPE
IDLE

     UMFI
     3013-391-NODIV

LISTTYPE
ACTIVE

     UMFI
     3013-391-NODIV

CELL
042C144

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
042C143

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
042C142

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
041C141

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
032C134

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
032C133

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
032C132

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
031C131

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
022C125

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
022C124

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
022C123

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
021C122

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
021C121

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
012C114

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
012C113

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
011C112

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
011C111

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360350

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360349

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360348

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360347

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360346

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360345

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360344

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360343

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360342

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
1360341

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360340

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360339

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360338

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360337

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
1360336

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360335

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360334

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360333

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360332

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360331

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360330

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360329

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
1360328

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360327

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360326

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360325

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360324

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360323

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360322

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360321

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360320

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
1360310

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360309

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360308

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360307

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360306

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360305

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360304

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360303

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360302

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
1360301

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360300

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360299

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360298

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360297

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
1360296

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360295

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360294

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360293

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360292

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360291

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360290

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360289

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
1360288

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360287

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360286

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360285

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360284

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360283

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360282

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360281

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1360280

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136130C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136130B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136130A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136129C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136129B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136129A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136128C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136128B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136128A

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
136127C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136127B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136127A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136126C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136126B

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136126A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136125C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136125B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136125A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136124C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136124B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136124A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136123A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136122C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136122B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136122A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136121C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136121B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136121A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136120C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136120B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136120A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136110C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136110B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136110A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136109C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136109B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136109A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136108C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136108B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136108A

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
136107C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136107B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136107A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136106C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136106B

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136106A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136105C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136105B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136105A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136104C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136104B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136104A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136103A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136102C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136102B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136102A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136101C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136101B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136101A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136100C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136100B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136100A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136090C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136090B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136090A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136089C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136089B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136089A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136088C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136088B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136088A

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
136087C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136087B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136087A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136086C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136086B

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136086A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136085C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136085B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136085A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136084C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136084B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136084A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136083A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136082C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136082B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136082A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136081C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136081B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136081A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136080C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136080B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136080A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136070C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136070B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136070A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136069C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136069B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136069A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136068C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136068B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136068A

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
136067C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136067B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136067A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136066C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136066B

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136066A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136065C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136065B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136065A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136064C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136064B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136064A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136063A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136062C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136062B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136062A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136061C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136061B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136061A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136060C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136060B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136060A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136050C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136050B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136050A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136049C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136049B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136049A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136048C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136048B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136048A

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
136047C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136047B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136047A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136046C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136046B

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136046A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136045C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136045B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136045A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136044C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136044B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136044A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136043A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136042C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136042B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136042A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136041C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136041B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136041A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136040C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136040B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136040A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136030C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136030B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136030A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136029C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136029B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136029A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136028C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136028B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136028A

LISTTYPE
IDLE

     UMFI
     130-256-NODIV
     130-488-DIV

LISTTYPE
ACTIVE

     UMFI
     130-256-NODIV
     130-488-DIV

CELL
136027C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136027B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136027A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136026C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136026B

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136026A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136025C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136025B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136025A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136024C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136024B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136024A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136023A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
136022C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136022B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136022A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136021C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136021B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136021A

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136020C

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136020B

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
136020A

LISTTYPE
IDLE

     UMFI
     128-256-NODIV
     128-488-DIV

LISTTYPE
ACTIVE

     UMFI
     128-256-NODIV
     128-488-DIV

CELL
1362C7

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1362C6

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1362C5

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1362C4

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1362C3

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1362C2

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1362C1

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1361C7

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1361C6

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1361C5

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1361C4

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1361C3

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1361C2

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI


CELL
1361C1

LISTTYPE
IDLE

     UMFI


LISTTYPE
ACTIVE

     UMFI

END


'''

    rlmbpAll = '''rlmbp:ID=all;
CELL BROADCAST SHORT MESSAGE SERVICE
MESSAGE DATA

ID     CODE  GS  UPDATE  MODE  LANG  MCO  MCL  NUMPAGES
50        1   0   1      MML     1              1

TEXT                                       PAGE
CELL 1361C1                                 1

ID     CODE  GS  UPDATE  MODE  LANG  MCO  MCL  NUMPAGES
50        2   0   1      MML     1              1

TEXT                                       PAGE
CELL 1361C2                                 1

ID     CODE  GS  UPDATE  MODE  LANG  MCO  MCL  NUMPAGES
50        3   0   1      MML     1              1

TEXT                                       PAGE
CELL 1361C3 aadddadadadada!adadadadadad     1
aaaaa

ID     CODE  GS  UPDATE  MODE  LANG  MCO  MCL  NUMPAGES
202       1   0   0      MML     1              4

TEXT                                       PAGE
aaa"AAA"   4A  "CC"                         1

4A  CC                                      2
5CC

PNO1P1O1                                    3*

END'''

    testHorizontal = '''
SOME SLOGAN

OBJECTID VERTPARAM1
1        VP1V

    VERTPARAM2
    VPV2
        
HORIZPARAM1: H1 H2 H3 HORIZPARAM2: BLABLA BLA

OBJECTID VERTPARAM1
2        VP1V2

    VERTPARAM2
    VPV22
        
HORIZPARAM1: H12 H22 H32 HORIZPARAM2: BLABLA BLA1

'''

    testJustify = '''
printout

ID PARAM1          PARAM2
1       3  3    BLABKLLLL

'''

    laeipAll = '''
laeip:suid=all;
REGIONAL SOFTWARE UNIT IDENTIFICATIONS

BLOCK   BN    SUNAME   SUID                             SUTYPE CNO PRIO
RPFD    H'191 RPFDR    9000/CXC 146 10        R1B01     RPD     20 
RDEX    H'1EA RDEXR    9000/CAA 140 067        R1B02    RPD      7 
TERT    H'17D TERTR    1/CAA 135 005          R1A02     RP2      3 
        H'0   EIEX1R   9000/CAA 203 58        R2B01     EMRPT  202 
FCT     H'105 FCTR     1/CAA 135 008          R1A01     RP2      3 
REX     H'1C3 REXR     1/CAA 135 003          R3A01     RP2      3 
C7GST   H'57A C7GSTR   9000/CXC 146 153       R1E01     RPD     19 
RPIFD   H'4C4 RPIFDR   9000/CXC 146 03        R1A08     RPD     19 
RPMBH   H'4D3 RPMBHR   1/CAA 135 2518/RPMBH   R1C02     RP2      3 
RPFD    H'191 RPFDR    9000/CXC 146 05        R1A03     RPD     19 
EXAL0   H'14E EXAL0R   2/CAA 117 045/1 E      R1A02     EMRP     1    0
TW      H'161 TWR      2/CAA 117 058/1 E      R1A01     EMRP     1    0
EXAL0   H'14E EXAL0R   1400/CAA 117 052/1B    R2A01     EMRP     1    0
TW      H'161 TWR      2/CAA 117 064/1 E      R1A01     EMRP     1    0
TW      H'161 TWR      9000/CAA 140 215/1K    R2D0A     EMRPD    6 
TW      H'161 TWR      0000/CAA 140 215/1K    R2A04     EMRPD    6 
INET    H'4F1 INETR    9000/CXC 146 09        R4B02     RPD     19 
EMGFD   H'196 EMGFDR   1402/CAA 117 054/1N    R3B01     EMRP     1    0
RGMAC   H'3F3 RGMACR   4/CXC 146 1797/6000    R1A08     RPD     19 
ETM2    H'2A6 ETM2R    9000/CXC 146 165       R1F01     RPD     20 
ETM3    H'2D0 ETM3R    9000/CXC 146 38        R2M01     RPD     20 
RPMM    H'4AA RPMMR    1/CAA 135 2517/RPMM    R1A01     RP2      3 
ETM3    H'2D0 ETM3R    9000/CXC 146 166       R1E01     RPD     20 
ETM4    H'688 ETM4R    8000/CXC 146 263       R2A07     RPD     19 
        H'0   ESEXR    9000/CAA 140 065       R1B03     EMRPD    6 
OCITS   H'1BC OCITSR   9000/CAA 140 194       R1B01     RPD     18 
RPFD    H'191 RPFDR    1/CAA 135 004/RPFD     R3A01     RP2      3 
SSTACK  H'4C6 SSTACKR  9000/CXC 146 01        R1B01     RPD     18 
SFRAME  H'4CD SFRAMER  9000/CXC 146 06        R1B02     RPD     19 
JOB     H'1   JOBR     9000/CXC 146 254       R3A01     RPD     19 
ETM5    H'69B ETM5R    9000/CXC 146 263       R2A07     RPD     19 
TEDC    H'1E8 TEDCR    CAA 140 013            R1B01     RPD      7 
RPFD    H'191 RPFDR    CAA 140 002            R7A01     RPD      7 
RAEX    H'4E7 RAEXR    9000/CXC 146 257       R2M01     RPD     26 
GPEX2   H'A0E GPEX2R   9000/CXC 146 256       R5G01     RPD     27 
FCT     H'105 FCTR     1/CXC 146 26           R2A01     RPD     19 
RDEX    H'1EA RDEXR    9000/CAA 140 066        R1B02    RPD      7 
FSI     H'466 FSIR     9000/CXC 146 07        R1A03     RPD     19 
TEDC    H'1E8 TEDCR    CAA 140 014            R1A03     EMRPD    6 
        H'0   EDEXR    CAA 140 063             R1B01    EMRPD    6 
RDEX    H'1EA RDEXR    CAA 140 067             R1B02    RPD      7 
        H'0   REPER    1401/CAA 117 2517/1N   R1B02     EMRP     1    0
        H'0   EDEXR    9000/CAA 140 063        R1B01    EMRPD    6 
EMGFD   H'196 EMGFDR   CAA 140 001             R7A01    EMRPD    6 
STCP    H'462 STCPR    9000/CAA 140 229       R1A03     RPD     18 
SFR     H'464 SFRR     9000/CAA 140 230       R1A02     RPD     18 
ETHDRV  H'467 ETHDRVR  9000/CAA 140 232       R1A03     RPD     18 
GSIDRV  H'465 GSIDRVR  9000/CAA 140 233       R1A02     RPD     18 
FSI     H'466 FSIR     9000/CAA 140 234       R3A02     RPD     18 
SSTR    H'463 SSTRR    9000/CAA 140 228       R1A02     RPD     18 
EMGFD   H'196 EMGFDR   9000/CAA 140 001        R7A01    EMRPD    6 
TEET    H'11A TEETR    1000/CAA 117 067/1N    R2A01     EMRP     1    0
        H'0   ESEXR    9000/CAA 140 078        R1B01    EMRPD    6 
JOB     H'1   JOBR     9000/CAA 140 090       R1A03     RPD     19 
        H'0   REPER    1/CAA 117 073/1        R2B01     EMRP     1    0
RDEX    H'1EA RDEXR    CAA 140 066             R1B02    RPD      7 
        H'0   REPER    1401/CAA 117 2516/1N   R1B02     EMRP     1    0
OCITS   H'1BC OCITSR   CAA 140 040             R1B01    RPD      7 
CSLSNT  H'4F8 CSLSNTR  9000/CAA 140 033       R2A01     RPD     18 
CSLM7   H'4F7 CSLM7R   9000/CAA 140 034       R5A02     RPD     18 
REX     H'1C3 REXR     1/CAA 135 2509/REX     R3B01     RP2      3 
RTEX    H'4D9 RTEXR    9000/CXC 146 22        R4A04     RPD     24 
EMGFD   H'196 EMGFDR   9000/CAA 140 007       R1A03     EMRPT  200 
TEET    H'11A TEETR    9000/CAA 140 054       R1A03     EMRPT  200 
INET    H'4F1 INETR    9000/CXC 146 40        R2E01     RPD     20 
RPIFD   H'4C4 RPIFDR   9000/CXC 146 23        R1A01     RPD     20 
SCBSNMP H'A22 SCBSNMPR 9000/CXC 146 143       R3A04     RPD     20 
FWRP    H'A03 RAEXFR   9000/CXC 152 0022      R4C01     RPD    610 
EMGFD   H'196 EMGFDR   CAA 140 018             R3A01    EMRPD    6 
INET    H'4F1 INETR    9000/CXC 146 089       R1E01     RPD     19 
FWRP    H'A03 GPEX2FR  9000/CXC 152 0026      R8D01     RPD    611 
JOB     H'1   JOBR     9000/CAA 140 087       R1A01     RPD     20 
EMGFD   H'196 EMGFDR   9000/CAA 140 062        R1A01    EMRPD    6 
OCITS   H'1BC OCITSR   9000/CXC 146 084       R2E01     RPD     19 
OCITS   H'1BC OCITSR   9000/CAA 140 1124      R1B01     RPD     20 
CSLSNT  H'4F8 CSLSNTR  9000/CXC 146 33        R1A01     RPD     20 
CSLM7   H'4F7 CSLM7R   9000/CXC 146 32        R1A02     RPD     20 
TW      H'161 TWR      9000/CAA 140 069       R1B01     EMRPT  200 
TEEMON  H'4DF TEEMONR  9000/CXC 146 39        R1A02     RPD     20 
INET    H'4F1 INETR    9000/CXC 146 151       R1C01     RPD     20 
INET    H'4F1 INETR    9000/CXC 146 125       R4G01     RPD     19 
INET    H'4F1 INETR    9000/CXC 146 591       R6F01     RPD     19 
RIEX    H'4E8 RIEXR    9000/CXC 146 147       R2L02     RPD     28 
CBEX    H'A4A CBEXR    9000/CXC 146 221       R4J01     RPD     31 
IP      H'59D IPR      9000/CXC 146 087       R3B02     RPD     19 
RPMM    H'4AA RPMMR    9000/CXC 146 20        R2B01     RPD     20 
RCCBC   H'662 RCCBCR   4/CXC 146 1732/4000    R1A02     RPD     19 
RGMAC   H'3F3 RGMACR   7/CXC 146 1797/6000    R1A08     RPD     19 
RPMBH   H'4D3 RPMBHR   9000/CXC 146 139       R1A04     RPD     19 
        H'0   EIEX1R   9000/CAA 203 58        R3D02     EMRPT  202 
RGMAC   H'3F3 RGMACR   8/CXC 146 1797/6000    R1A08     RPD     30 
RCCBC   H'662 RCCBCR   7/CXC 146 1732/4000    R1A02     RPD     19 
RCCBC   H'662 RCCBCR   8/CXC 146 1732/4000    R1A02     RPD     30 
RCLCCH  H'24E RCLCCHR  3/CXC 146 1759/5100    R1A01     RPD     20 
SFRAME  H'4CD SFRAMER  9000/CXC 146 48        R1C02     RPD     19 
RCLCCH  H'24E RCLCCHR  7/CXC 146 1759/5100    R1A01     RPD     19 
RCLCCH  H'24E RCLCCHR  8/CXC 146 1759/5100    R1A01     RPD     30 
INET    H'4F1 INETR    9000/CXC 146 159       R1A01     RPD     20 
SFRAME  H'4CD SFRAMER  9000/CXC 146 120       R1C02     RPD     19 
RGCON   H'3F2 RGCONR   4/CXC 146 1796/6000    R1A02     RPD     19 
RGCON   H'3F2 RGCONR   7/CXC 146 1796/6000    R1A02     RPD     19 
RGCON   H'3F2 RGCONR   8/CXC 146 1796/6000    R1A02     RPD     30 
RTPGS   H'561 RTPGSR   6/CXC 146 1782/6000    R1A02     RPD     19 
RPMBH   H'4D3 RPMBHR   9000/CXC 146 21        R6A06     RPD     20 
FWRP    H'A03 GPEXFR   9000/CXC 152 0015      R3B01     RPD    609 
GPEX    H'A06 GPEXR    9000/CXC 146 092       R8L01     RPD     25 
RTPGS   H'561 RTPGSR   7/CXC 146 1782/6000    R1A02     RPD     19 
RTPGS   H'561 RTPGSR   8/CXC 146 1782/6000    R1A02     RPD     30 
RHLAPD  H'A8  RHLAPDR  3/CXC 146 1777/6000    R1A01     RPD     20 
INET    H'4F1 INETR    9000/CXC 146 600       R1E01     RPD     30 
RGRLC   H'393 RGRLCR   4/CXC 146 1794/6000    R1A02     RPD     19 
RGRLC   H'393 RGRLCR   7/CXC 146 1794/6000    R1A02     RPD     19 
RCSCB2  H'661 RCSCB2R  3/CXC 146 1761/5000    R1A01     RPD     20 
CLM     H'3C9 CLMR     9000/CXC 146 30        R1S01     RPD     20 
RCSCB2  H'661 RCSCB2R  7/CXC 146 1761/5000    R1A01     RPD     19 
RCSCB2  H'661 RCSCB2R  8/CXC 146 1761/5000    R1A01     RPD     30 
RCSCB   H'D7  RCSCBR   3/CXC 146 1760/5000    R1A01     RPD     20 
RCSCB   H'D7  RCSCBR   7/CXC 146 1760/5000    R1A01     RPD     19 
RCSCB   H'D7  RCSCBR   8/CXC 146 1760/5000    R1A01     RPD     30 
RGCNT   H'52D RGCNTR   4/CXC 146 1748/5000    R1A25     RPD     19 
RGCNT   H'52D RGCNTR   7/CXC 146 1748/5000    R1A25     RPD     19 
RGCNT   H'52D RGCNTR   8/CXC 146 1748/5000    R1A25     RPD     30 
RHLAPD  H'A8  RHLAPDR  7/CXC 146 1777/6000    R1A01     RPD     19 
S7GST   H'604 S7GSTR   9000/CXC 146 158       R1B01     RPD     19 
C7GSTAH H'57D C7GSTAHR 9000/CXC 146 156       R1C01     RPD     19 
XM      H'3D2 XMR      9000/CXC 146 31        R3B01     RPD     20 
RGRLC   H'393 RGRLCR   8/CXC 146 1794/6000    R1A02     RPD     30 
RHLAPD  H'A8  RHLAPDR  8/CXC 146 1777/6000    R1A01     RPD     30 
RGNCC   H'55A RGNCCR   4/CXC 146 1751/5000    R1A01     RPD     19 
RGNCC   H'55A RGNCCR   7/CXC 146 1751/5000    R1A01     RPD     19 
RGNCC   H'55A RGNCCR   8/CXC 146 1751/5000    R1A01     RPD     30 
EBEX    H'A43 EBEXR    9000/CXC 146 252       R4H01     RPD     29 
C7STH   H'3E7 C7STHR   9000/CXC 146 08        R2B01     RPD     19 
C7GSTH  H'57B C7GSTHR  9000/CXC 146 154       R1B01     RPD     19 
AUCM    H'689 AUCMR    9000/CXC 146 226       R1D01     RPD     19 
RGSERV  H'395 RGSERVR  4/CXC 146 1746/5000    R1A01     RPD     19 
RGSERV  H'395 RGSERVR  7/CXC 146 1746/5000    R1A01     RPD     19 
RGSERV  H'395 RGSERVR  8/CXC 146 1746/5000    R1A01     RPD     30 
RHTRH   H'572 RHTRHR   3/CXC 146 1766/5000    R1A02     RPD     20 
RHTRH   H'572 RHTRHR   7/CXC 146 1766/5000    R1A02     RPD     19 
ROAFLP  H'704 ROAFLPR  7/CXC 146 1735/5000    R1A01     RPD     19 
ROAFLP  H'704 ROAFLPR  8/CXC 146 1735/5000    R1A01     RPD     30 
ROCTH   H'681 ROCTHR   8/CXC 146 1744/5000    R1A02     RPD     30 
S7HST   H'605 S7HSTR   9000/CXC 146 157       R1A03     RPD     19 
ROFW    H'63B ROFWR    7/CXC 146 1757/5000    R1A01     RPD     19 
ROGSHCS H'700 ROGSHCSR 7/CXC 146 1737/5000    R1A01     RPD     19 
MUX34   H'3CC MUX34R   9000/CXC 146 44        R2D05     RPD     20 
ROGSHCS H'700 ROGSHCSR 8/CXC 146 1737/5000    R1A01     RPD     30 
GCRLC   H'591 GCRLCR   4/CXC 146 1326/6400    R1D01     RPD     19 
ETM2    H'2A6 ETM2R    9000/CXC 146 45        R3T01     RPD     20 
EMUX    H'554 EMUXR    9000/CXC 146 077       R2A01     RPD     20 
ROGSH   H'69F ROGSHR   7/CXC 146 1738/5000    R1A02     RPD     19 
RTGBPGI H'601 RTGBPGIR 4/CXC 146 1329/6400    R1B01     RPD     19 
RTTF1S1 H'37F RTTF1S1R 1/CAA 135 3072         R2A01     RP2      3 
RTTF1S2 H'38A RTTF1S2R 1/CAA 135 3073         R2A01     RP2      3 
C7ST2   H'73  C7ST2R   1/CAA 105 2501/C7ST2   R1A03     RP2      3 
C7ST2C  H'30F C7ST2CR  CAA 140 053/S23A       R3A03     RPD     18 
CLT     H'50  CLTR     2/CAA 105 1528/CLT     R1A01     RP2      3 
ETRALT4 H'254 ETRALT4R 1/CAA 135 1081/ETRALT4 R3A01     RP2      3 
ETRALT  H'77  ETRALTR  1/CAA 135 3024/ETRALT  R3A02     RP2      3 
ETRBLT4 H'253 ETRBLT4R 1/CAA 135 1081/ETRBLT4 R3A01     RP2      3 
ETRBLT  H'85  ETRBLTR  1/CAA 135 3024/ETRBLT  R3A02     RP2      3 
ETRTB4  H'368 ETRTB4R  1/CAA 135 1081/ETRTB4  R3A01     RP2      3 
ETRTB   H'367 ETRTBR   1/CAA 135 3024/ETRTB   R3A02     RP2      3 
ETRTG4  H'39A ETRTG4R  1/CAA 135 1081/ETRTG4  R3A01     RP2      3 
ETRTG   H'399 ETRTGR   1/CAA 135 3024/ETRTG   R3A02     RP2      3 
ETRTL4  H'3FE ETRTL4R  1/CAA 135 1081/ETRTL4  R3A01     RP2      3 
ETRTL   H'2AE ETRTLR   1/CAA 135 3024/ETRTL   R3A02     RP2      3 
ETRTT4  H'366 ETRTT4R  1/CAA 135 1081/ETRTT4  R3A01     RP2      3 
ETRTT   H'365 ETRTTR   1/CAA 135 3024/ETRTT   R3A02     RP2      3 
ROGSH   H'69F ROGSHR   8/CXC 146 1738/5000    R1A02     RPD     30 
RTTAH1S H'524 RTTAH1SR 1/CAA 135 3071         R2A01     RP2      3 
RTTH1S  H'38C RTTH1SR  1/CAA 135 3074         R2A01     RP2      3 
GCCGHS  H'592 GCCGHSR  4/CXC 146 1324/6400    R1A01     RPD     19 
RTTAF1S H'523 RTTAF1SR 1/CAA 135 3070         R2A01     RP2      3 
GCPGHS  H'593 GCPGHSR  4/CXC 146 1325/6400    R1A01     RPD     19 
S7STH   H'52A S7STHR   9000/CXC 146 100       R1B01     RPD     19 
MUXTS   H'3CE MUXTSR   1/CAA 135 3060         R2A04     RP2      3 
S7STG   H'389 S7STGR   9000/CXC 146 36        R2A01     RPD     20 
S7STG   H'389 S7STGR   9000/CAA 140 048/3A     R1A04    RPD     18 
S7ST    H'275 S7STR    1/CAAU 135 0001/S7ST   R1A02     RP2      3 
SRS     H'338 SRSR     1/CAA 135 3016/SRS     R2A01     RP2      3 
TSM     H'51  TSMR     1/CAA 135 3039/TSM     R2A04     RP2      3 
RICS    H'9C  RICSR    1946/CAA 117 1109/B07C R1A05     EMRP     1    0
RILCO   H'283 RILCOR   CAA 140 1021 R1A08               EMRPD    6 
RILT    H'94  RILTR    1946/CAA 117 1108/B07C R1A06     EMRP     1    0
RITS    H'9D  RITSR    1946/CAA 117 1110/B07D R2A01     EMRP     1    0
RTTF1S1 H'37F RTTF1S1D CXCW 200 001             R3D02   DP       8 
RTTF1S2 H'38A RTTF1S2D CXCW 200 002             R3G01   DP       8 
RTTH1S  H'38C RTTH1SD  CXCW 200 003             R3E03   DP       8 
GCCGH   H'58F GCCGHR   4/CXC 146 1292/6900    R1A01     RPD     19 
C7ST2C  H'30F C7ST2CR  9000/CXC 146 37        R2A01     RPD     20 
RTTAH1S H'524 RTTAH1SD CXCW 201 010             R2C01   DP       8 
GCURR   H'586 GCURRR   5/CXC 146 1318/6900    R1A01     RPD     19 
GCSGHS  H'594 GCSGHSR  5/CXC 146 1324/6400    R1A01     RPD     19 
RTTAF1S H'523 RTTAF1SD CXCW 201 011             R2C01   DP       8 
RTIPCGH H'55B RTIPCGHR 4/CXC 146 1327/6400    R1A01     RPD     19 
RTIPSGH H'55D RTIPSGHR 5/CXC 146 1327/6400    R1A01     RPD     19 
RTPGAH  H'602 RTPGAHR  4/CXC 146 1330/6400    R1A01     RPD     19 
C7STAH  H'2EE C7STAHR  9000/CXC 146 34        R1E01     RPD     19 
RTAGWFW H'64F RTAGWFWR 7/CXC 146 1771/5000    R1A02     RPD     19 
RTAGW   H'647 RTAGWR   7/CXC 146 1768/5000    R1A01     RPD     19 
RTAGW   H'647 RTAGWR   8/CXC 146 1768/5000    R1A01     RPD     30 
RTAGWS  H'650 RTAGWSR  7/CXC 146 1769/5000    R1A01     RPD     19 
RTPGCS  H'56A RTPGCSR  6/CXC 146 1741/5000    R1A01     RPD     19 
RTPGCS  H'56A RTPGCSR  7/CXC 146 1741/5000    R1A01     RPD     19 
RTPGWFW H'64E RTPGWFWR 7/CXC 146 1743/5000    R1A02     RPD     19 
RMPAG   H'DE  RMPAGR   3/CXC 146 1765/5100    R1A01     RPD     20 
RMPAG   H'DE  RMPAGR   7/CXC 146 1765/5100    R1A01     RPD     19 
RMPAG   H'DE  RMPAGR   8/CXC 146 1765/5100    R1A01     RPD     30 
RQRCQS  H'250 RQRCQSR  3/CXC 146 1763/5100    R1A03     RPD     20 
RQRCQS  H'250 RQRCQSR  7/CXC 146 1763/5100    R1A03     RPD     19 
RQRCQS  H'250 RQRCQSR  8/CXC 146 1763/5100    R1A03     RPD     30 
RQUNC   H'23F RQUNCR   3/CXC 146 1764/5100    R1A01     RPD     20 
RQUNC   H'23F RQUNCR   7/CXC 146 1764/5100    R1A01     RPD     19 
RQUNC   H'23F RQUNCR   8/CXC 146 1764/5100    R1A01     RPD     30 
RTGBIP  H'53E RTGBIPR  4/CXC 146 1755/5100    R1A05     RPD     19 
RTGBIP  H'53E RTGBIPR  7/CXC 146 1755/5100    R1A05     RPD     19 
RTGBIP  H'53E RTGBIPR  8/CXC 146 1755/5100    R1A05     RPD     30 
RTGB    H'38F RTGBR    4/CXC 146 1756/5100    R1A05     RPD     19 
RTGB    H'38F RTGBR    7/CXC 146 1756/5100    R1A05     RPD     19 
RTTG1S  H'569 RTTG1SR  9000/CXCW 201 024      R1F01     RPD     20 
RTTGS   H'3D9 RTTGSR   9000/CXCW 201 023      R1F01     RPD     20 
RGEX    H'456 RGEXR    9000/CXC 146 27        R5J02     RPD     22 
RIEX    H'4E8 RIEXR    9000/CXC 146 097       R6G01     RPD     21 
SCBSWMG H'A23 SCBSWMGR 9000/CXC 146 145       R2F01     RPD     20 
ROANRH  H'70C ROANRHR  7/CXC 146 1672/4000    R1A01     RPD     19 
ROANRH  H'70C ROANRHR  8/CXC 146 1672/4000    R1A01     RPD     30 
RPEX    H'4BE RPEXR    9000/CXC 146 070       R5H01     RPD     19 
RTGPHDV H'391 RTGPHDVR 4/CXC 146 1734/4000    R1A01     RPD     19 
RTGPHDV H'391 RTGPHDVR 7/CXC 146 1734/4000    R1A01     RPD     19 
RTGPHDV H'391 RTGPHDVR 8/CXC 146 1734/4000    R1A01     RPD     30 
RTIPAGW H'649 RTIPAGWR 7/CXC 146 1659/4000    R1A01     RPD     19 
RTIPCTH H'682 RTIPCTHR 8/CXC 146 1665/4000    R1A01     RPD     30 
RTIPGPH H'533 RTIPGPHR 4/CXC 146 1712/4000    R1A01     RPD     19 
RTIPGPH H'533 RTIPGPHR 7/CXC 146 1712/4000    R1A01     RPD     19 
RTIPGPH H'533 RTIPGPHR 8/CXC 146 1712/4000    R1A01     RPD     30 
RTIPGSH H'701 RTIPGSHR 7/CXC 146 1664/4000    R1A01     RPD     19 
RTIPGSH H'701 RTIPGSHR 8/CXC 146 1664/4000    R1A01     RPD     30 
RTIPPGW H'55E RTIPPGWR 6/CXC 146 1652/4000    R1A01     RPD     19 
RTIPPGW H'55E RTIPPGWR 7/CXC 146 1652/4000    R1A01     RPD     19 
RTIPTRH H'611 RTIPTRHR 7/CXC 146 1696/4000    R1A01     RPD     19 
SCTP    H'59B SCTPR    9000/CXC 146 202       R6C02     RPD     19 
END


'''


    nsdap = '''
NSDAP;
CLOCK-REFERENCE SUPERVISION DATA

AREA
OPERATING

STATIC DATA

REF               CLREFINL  REFGRP  PRI     FDL  WDL  ACL
EXT-0                    0       1    3   10000   95   A2
123,MS-1                 1            4    2000   85   A1

DYNAMIC DATA

REF         FD  WD FREQMEM  FREQDRIFTMEM
dip         fd  wd freqmem  freqdriftmem

END
'''

    nsdap2 = '''NSDAP;
CLOCK-REFERENCE SUPERVISION DATA

AREA
OPERATING

STATIC DATA

REF               CLREFINL  REFGRP  PRI     FDL  WDL  ACL
EXT-0                    0       1    1   10000   95   A2

DYNAMIC DATA

REF                  FD    WD
EXT-0                 0     0

END'''


    exrppAll = '''
exrpp:rp=all;
RP DATA

RP    STATE  TYPE     TWIN  STATE   DS     MAINT.STATE  PIU
   0  AB     RPSCB1E                       IDLE
   1  AB     RPSCB1E                       IDLE
  32  WO     RPSCB1E                       IDLE
  33  WO     RPSCB1E                       IDLE
  34  WO     RPI2E                         IDLE
  35  WO     RPI2E                         IDLE
  37  WO     GARP2E                        IDLE
  39  WO     GARP2E                        IDLE
  40  WO     GARP2E                        IDLE
  41  WO     GARP2E                        IDLE
  42  WO     GARP2E                        IDLE
  43  WO     GARP2E                        IDLE
  44  WO     GARP2E                        IDLE
  46  WO     GARP2E                        IDLE
  48  WO     GARP2E                        IDLE
  50  WO     RPI2E                         IDLE
  51  WO     RPI2E                         IDLE
  54  WO     RPI2E                         IDLE
  64  WO     RPSCB1E                       IDLE
  65  WO     RPSCB1E                       IDLE
  66  WO     RPI2E                         IDLE
  67  WO     RPI2E                         IDLE
  69  WO     GARP2E                        IDLE
  71  WO     GARP2E                        IDLE
  72  WO     GARP1E                        IDLE
  73  WO     GARP2E                        IDLE
  74  WO     GARP1E                        IDLE
  75  WO     GARP2E                        IDLE
  76  WO     GARP2E                        IDLE
  77  WO     GARP2E                        IDLE
  78  WO     GARP2E                        IDLE
  79  WO     GARP2E                        IDLE
  80  WO     GARP2E                        IDLE
  81  WO     GARP2E                        IDLE
  82  WO     GARP2E                        IDLE
  83  WO     GARP2E                        IDLE
  86  WO     RPI2E                         IDLE

END


'''

    rlvgpAll = """RLVGP:CELL=ALL;
CELL VOICE GROUP CALL SERVICE DATA

PMRSUPP  PAGPRIO  VGPRIO  NOTIFP  TALKID  DISPP  VGENCR
ON       5        15      30      OFF     30     OFF

CELL      REPPERNCH  VGCHALLOC   FBVGCHALLOC  CHMAX  DYNVGCH

NONE

END
"""


    rlnrpAll= '''RLNRP:CELL=ALL,UTRAN;
NEIGHBOUR RELATION DATA

CELL
112C202

CELLR     DIR
NONE

CELL
111C201

CELLR     DIR
NONE

CELL
092C188

CELLR     DIR
NONE

CELL
091C187

CELLR     DIR
NONE

CELL
092C186

CELLR     DIR
NONE

CELL
091C185

CELLR     DIR
NONE

CELL
082C180

CELLR     DIR
NONE

CELL
082C179

CELLR     DIR
D013C1    SINGLE

CELL
082C178

CELLR     DIR
D013C1    SINGLE

CELL
081C177

CELLR     DIR
D013C1    SINGLE

CELL
072C172

CELLR     DIR
NONE

CELL
072C171

CELLR     DIR
D039C1    SINGLE

CELL
072C170

CELLR     DIR
D039C1    SINGLE

CELL
071C169

CELLR     DIR
D039C1    SINGLE

CELL
042C144

CELLR     DIR
NONE

CELL
042C143

CELLR     DIR
NONE

CELL
042C142

CELLR     DIR
NONE

CELL
041C141

CELLR     DIR
NONE

CELL
032C134

CELLR     DIR
NONE

CELL
032C133

CELLR     DIR
NONE

CELL
032C132

CELLR     DIR
NONE

CELL
031C131

CELLR     DIR
NONE

CELL
022C125

CELLR     DIR
NONE

CELL
022C124

CELLR     DIR
NONE

CELL
022C123

CELLR     DIR
NONE

CELL
021C122

CELLR     DIR
NONE

CELL
021C121

CELLR     DIR
NONE

CELL
012C114

CELLR     DIR
NONE

CELL
012C113

CELLR     DIR
NONE

CELL
011C112

CELLR     DIR
NONE

CELL
011C111

CELLR     DIR
NONE

CELL
1360350

CELLR     DIR
NONE

CELL
1360349

CELLR     DIR
NONE

CELL
1360348

CELLR     DIR
NONE

CELL
1360347

CELLR     DIR
NONE

CELL
1360346

CELLR     DIR
NONE

CELL
1360345

CELLR     DIR
NONE

CELL
1360344

CELLR     DIR
NONE

CELL
1360343

CELLR     DIR
NONE

CELL
1360342

CELLR     DIR
NONE

CELL
1360341

CELLR     DIR
NONE

CELL
1360340

CELLR     DIR
NONE

CELL
1360339

CELLR     DIR
NONE

CELL
1360338

CELLR     DIR
NONE

CELL
1360337

CELLR     DIR
NONE

CELL
1360336

CELLR     DIR
NONE

CELL
1360335

CELLR     DIR
NONE

CELL
1360334

CELLR     DIR
NONE

CELL
1360333

CELLR     DIR
NONE

CELL
1360332

CELLR     DIR
NONE

CELL
1360331

CELLR     DIR
NONE

CELL
1360330

CELLR     DIR
NONE

CELL
1360329

CELLR     DIR
NONE

CELL
1360328

CELLR     DIR
NONE

CELL
1360327

CELLR     DIR
NONE

CELL
1360326

CELLR     DIR
NONE

CELL
1360325

CELLR     DIR
NONE

CELL
1360324

CELLR     DIR
NONE

CELL
1360323

CELLR     DIR
NONE

CELL
1360322

CELLR     DIR
NONE

CELL
1360321

CELLR     DIR
NONE

CELL
1360320

CELLR     DIR
NONE

CELL
1360310

CELLR     DIR
NONE

CELL
1360309

CELLR     DIR
NONE

CELL
1360308

CELLR     DIR
NONE

CELL
1360307

CELLR     DIR
NONE

CELL
1360306

CELLR     DIR
NONE

CELL
1360305

CELLR     DIR
NONE

CELL
1360304

CELLR     DIR
NONE

CELL
1360303

CELLR     DIR
NONE

CELL
1360302

CELLR     DIR
NONE

CELL
1360301

CELLR     DIR
NONE

CELL
1360300

CELLR     DIR
NONE

CELL
1360299

CELLR     DIR
NONE

CELL
1360298

CELLR     DIR
NONE

CELL
1360297

CELLR     DIR
NONE

CELL
1360296

CELLR     DIR
NONE

CELL
1360295

CELLR     DIR
NONE

CELL
1360294

CELLR     DIR
NONE

CELL
1360293

CELLR     DIR
NONE

CELL
1360292

CELLR     DIR
NONE

CELL
1360291

CELLR     DIR
NONE

CELL
1360290

CELLR     DIR
NONE

CELL
1360289

CELLR     DIR
NONE

CELL
1360288

CELLR     DIR
NONE

CELL
1360287

CELLR     DIR
NONE

CELL
1360286

CELLR     DIR
NONE

CELL
1360285

CELLR     DIR
NONE

CELL
1360284

CELLR     DIR
NONE

CELL
1360283

CELLR     DIR
NONE

CELL
1360282

CELLR     DIR
NONE

CELL
1360281

CELLR     DIR
NONE

CELL
1360280

CELLR     DIR
NONE

CELL
136130C

CELLR     DIR
NONE

CELL
136130B

CELLR     DIR
NONE

CELL
136130A

CELLR     DIR
NONE

CELL
136129C

CELLR     DIR
NONE

CELL
136129B

CELLR     DIR
NONE

CELL
136129A

CELLR     DIR
NONE

CELL
136128C

CELLR     DIR
NONE

CELL
136128B

CELLR     DIR
NONE

CELL
136128A

CELLR     DIR
NONE

CELL
136127C

CELLR     DIR
NONE

CELL
136127B

CELLR     DIR
NONE

CELL
136127A

CELLR     DIR
NONE

CELL
136126C

CELLR     DIR
NONE

CELL
136126B

CELLR     DIR
NONE

CELL
136126A

CELLR     DIR
NONE

CELL
136125C

CELLR     DIR
NONE

CELL
136125B

CELLR     DIR
NONE

CELL
136125A

CELLR     DIR
NONE

CELL
136124C

CELLR     DIR
NONE

CELL
136124B

CELLR     DIR
NONE

CELL
136124A

CELLR     DIR
NONE

CELL
136123A

CELLR     DIR
NONE

CELL
136122C

CELLR     DIR
NONE

CELL
136122B

CELLR     DIR
NONE

CELL
136122A

CELLR     DIR
NONE

CELL
136121C

CELLR     DIR
NONE

CELL
136121B

CELLR     DIR
NONE

CELL
136121A

CELLR     DIR
NONE

CELL
136120C

CELLR     DIR
NONE

CELL
136120B

CELLR     DIR
NONE

CELL
136120A

CELLR     DIR
NONE

CELL
136110C

CELLR     DIR
NONE

CELL
136110B

CELLR     DIR
NONE

CELL
136110A

CELLR     DIR
NONE

CELL
136109C

CELLR     DIR
NONE

CELL
136109B

CELLR     DIR
NONE

CELL
136109A

CELLR     DIR
NONE

CELL
136108C

CELLR     DIR
NONE

CELL
136108B

CELLR     DIR
NONE

CELL
136108A

CELLR     DIR
NONE

CELL
136107C

CELLR     DIR
NONE

CELL
136107B

CELLR     DIR
NONE

CELL
136107A

CELLR     DIR
NONE

CELL
136106C

CELLR     DIR
NONE

CELL
136106B

CELLR     DIR
NONE

CELL
136106A

CELLR     DIR
NONE

CELL
136105C

CELLR     DIR
NONE

CELL
136105B

CELLR     DIR
NONE

CELL
136105A

CELLR     DIR
NONE

CELL
136104C

CELLR     DIR
NONE

CELL
136104B

CELLR     DIR
NONE

CELL
136104A

CELLR     DIR
NONE

CELL
136103A

CELLR     DIR
NONE

CELL
136102C

CELLR     DIR
NONE

CELL
136102B

CELLR     DIR
NONE

CELL
136102A

CELLR     DIR
NONE

CELL
136101C

CELLR     DIR
NONE

CELL
136101B

CELLR     DIR
NONE

CELL
136101A

CELLR     DIR
NONE

CELL
136100C

CELLR     DIR
NONE

CELL
136100B

CELLR     DIR
NONE

CELL
136100A

CELLR     DIR
NONE

CELL
136090C

CELLR     DIR
NONE

CELL
136090B

CELLR     DIR
NONE

CELL
136090A

CELLR     DIR
NONE

CELL
136089C

CELLR     DIR
NONE

CELL
136089B

CELLR     DIR
NONE

CELL
136089A

CELLR     DIR
NONE

CELL
136088C

CELLR     DIR
NONE

CELL
136088B

CELLR     DIR
NONE

CELL
136088A

CELLR     DIR
NONE

CELL
136087C

CELLR     DIR
NONE

CELL
136087B

CELLR     DIR
NONE

CELL
136087A

CELLR     DIR
NONE

CELL
136086C

CELLR     DIR
NONE

CELL
136086B

CELLR     DIR
NONE

CELL
136086A

CELLR     DIR
NONE

CELL
136085C

CELLR     DIR
NONE

CELL
136085B

CELLR     DIR
NONE

CELL
136085A

CELLR     DIR
NONE

CELL
136084C

CELLR     DIR
NONE

CELL
136084B

CELLR     DIR
NONE

CELL
136084A

CELLR     DIR
NONE

CELL
136083A

CELLR     DIR
NONE

CELL
136082C

CELLR     DIR
NONE

CELL
136082B

CELLR     DIR
NONE

CELL
136082A

CELLR     DIR
NONE

CELL
136081C

CELLR     DIR
NONE

CELL
136081B

CELLR     DIR
NONE

CELL
136081A

CELLR     DIR
NONE

CELL
136080C

CELLR     DIR
NONE

CELL
136080B

CELLR     DIR
NONE

CELL
136080A

CELLR     DIR
NONE

CELL
136070C

CELLR     DIR
NONE

CELL
136070B

CELLR     DIR
NONE

CELL
136070A

CELLR     DIR
NONE

CELL
136069C

CELLR     DIR
NONE

CELL
136069B

CELLR     DIR
NONE

CELL
136069A

CELLR     DIR
NONE

CELL
136068C

CELLR     DIR
NONE

CELL
136068B

CELLR     DIR
NONE

CELL
136068A

CELLR     DIR
NONE

CELL
136067C

CELLR     DIR
NONE

CELL
136067B

CELLR     DIR
NONE

CELL
136067A

CELLR     DIR
NONE

CELL
136066C

CELLR     DIR
NONE

CELL
136066B

CELLR     DIR
NONE

CELL
136066A

CELLR     DIR
NONE

CELL
136065C

CELLR     DIR
NONE

CELL
136065B

CELLR     DIR
NONE

CELL
136065A

CELLR     DIR
NONE

CELL
136064C

CELLR     DIR
NONE

CELL
136064B

CELLR     DIR
NONE

CELL
136064A

CELLR     DIR
NONE

CELL
136063A

CELLR     DIR
NONE

CELL
136062C

CELLR     DIR
NONE

CELL
136062B

CELLR     DIR
NONE

CELL
136062A

CELLR     DIR
NONE

CELL
136061C

CELLR     DIR
NONE

CELL
136061B

CELLR     DIR
NONE

CELL
136061A

CELLR     DIR
NONE

CELL
136060C

CELLR     DIR
NONE

CELL
136060B

CELLR     DIR
NONE

CELL
136060A

CELLR     DIR
NONE

CELL
136050C

CELLR     DIR
NONE

CELL
136050B

CELLR     DIR
NONE

CELL
136050A

CELLR     DIR
NONE

CELL
136049C

CELLR     DIR
NONE

CELL
136049B

CELLR     DIR
NONE

CELL
136049A

CELLR     DIR
NONE

CELL
136048C

CELLR     DIR
NONE

CELL
136048B

CELLR     DIR
NONE

CELL
136048A

CELLR     DIR
NONE

CELL
136047C

CELLR     DIR
NONE

CELL
136047B

CELLR     DIR
NONE

CELL
136047A

CELLR     DIR
NONE

CELL
136046C

CELLR     DIR
NONE

CELL
136046B

CELLR     DIR
NONE

CELL
136046A

CELLR     DIR
NONE

CELL
136045C

CELLR     DIR
NONE

CELL
136045B

CELLR     DIR
NONE

CELL
136045A

CELLR     DIR
NONE

CELL
136044C

CELLR     DIR
NONE

CELL
136044B

CELLR     DIR
NONE

CELL
136044A

CELLR     DIR
NONE

CELL
136043A

CELLR     DIR
NONE

CELL
136042C

CELLR     DIR
NONE

CELL
136042B

CELLR     DIR
NONE

CELL
136042A

CELLR     DIR
NONE

CELL
136041C

CELLR     DIR
NONE

CELL
136041B

CELLR     DIR
NONE

CELL
136041A

CELLR     DIR
NONE

CELL
136040C

CELLR     DIR
NONE

CELL
136040B

CELLR     DIR
NONE

CELL
136040A

CELLR     DIR
NONE

CELL
136030C

CELLR     DIR
NONE

CELL
136030B

CELLR     DIR
NONE

CELL
136030A

CELLR     DIR
NONE

CELL
136029C

CELLR     DIR
NONE

CELL
136029B

CELLR     DIR
NONE

CELL
136029A

CELLR     DIR
NONE

CELL
136028C

CELLR     DIR
NONE

CELL
136028B

CELLR     DIR
NONE

CELL
136028A

CELLR     DIR
NONE

CELL
136027C

CELLR     DIR
NONE

CELL
136027B

CELLR     DIR
NONE

CELL
136027A

CELLR     DIR
NONE

CELL
136026C

CELLR     DIR
NONE

CELL
136026B

CELLR     DIR
NONE

CELL
136026A

CELLR     DIR
NONE

CELL
136025C

CELLR     DIR
NONE

CELL
136025B

CELLR     DIR
NONE

CELL
136025A

CELLR     DIR
NONE

CELL
136024C

CELLR     DIR
NONE

CELL
136024B

CELLR     DIR
NONE

CELL
136024A

CELLR     DIR
NONE

CELL
136023A

CELLR     DIR
NONE

CELL
136022C

CELLR     DIR
NONE

CELL
136022B

CELLR     DIR
NONE

CELL
136022A

CELLR     DIR
NONE

CELL
136021C

CELLR     DIR
NONE

CELL
136021B

CELLR     DIR
NONE

CELL
136021A

CELLR     DIR
NONE

CELL
136020C

CELLR     DIR
NONE

CELL
136020B

CELLR     DIR
NONE

CELL
136020A

CELLR     DIR
NONE

CELL
1362C7

CELLR     DIR
NONE

CELL
1362C6

CELLR     DIR
NONE

CELL
1362C5

CELLR     DIR
NONE

CELL
1362C4

CELLR     DIR
NONE

CELL
1362C3

CELLR     DIR
NONE

CELL
1362C2

CELLR     DIR
NONE

CELL
1362C1

CELLR     DIR
NONE

CELL
1361C7

CELLR     DIR
NONE

CELL
1361C6

CELLR     DIR
NONE

CELL
1361C5

CELLR     DIR
NONE

CELL
1361C4

CELLR     DIR
NONE

CELL
1361C3

CELLR     DIR
NONE

CELL
1361C2

CELLR     DIR
NONE

CELL
1361C1

CELLR     DIR
NONE
END
'''


    testNone = '''
SOME PRINTOUT

HEADER1 HEADER2
NONE

END
'''

    tptipAll = '''
tptip:sdip=all;
SYNCHRONOUS DIGITAL PATH TRAIL TRACE IDENTIFIER DETAILS

SDIP     LAYER    TIMMODE   TYPE  TTI
0SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
0SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3


SDIP     LAYER    TIMMODE   TYPE  TTI
1SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
1SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3


SDIP     LAYER    TIMMODE   TYPE  TTI
2SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
2SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3


SDIP     LAYER    TIMMODE   TYPE  TTI
3SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
3SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3


SDIP     LAYER    TIMMODE   TYPE  TTI
4SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
4SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3


SDIP     LAYER    TIMMODE   TYPE  TTI
5SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
5SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3


SDIP     LAYER    TIMMODE   TYPE  TTI
6SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
6SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3


SDIP     LAYER    TIMMODE   TYPE  TTI
7SDIPM4  VC4-0    DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-0   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-1   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-2   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-3   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-4   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-5   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-6   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-7   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-8   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-9   DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-10  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-11  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-12  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-13  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-14  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-15  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-16  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-17  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-18  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-19  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-20  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-21  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-22  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-23  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-24  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-25  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-26  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-27  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-28  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-29  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-30  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-31  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-32  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-33  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-34  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-35  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-36  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-37  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-38  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-39  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-40  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-41  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-42  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-43  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-44  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-45  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-46  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-47  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-48  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-49  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-50  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-51  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-52  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-53  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-54  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-55  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-56  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-57  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-58  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-59  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-60  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-61  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000
         VC12-62  DISABLED  T     
                                  H'00000000000000000000000000000000
                            E     
                                  H'00000000000000000000000000000000
                            R     NOT VALID
                                  H'00000000000000000000000000000000


SDIP     LAYER    K  L  M
7SDIPM4  VC4-0
         VC12-0   1  1  1
         VC12-1   2  1  1
         VC12-2   3  1  1
         VC12-3   1  2  1
         VC12-4   2  2  1
         VC12-5   3  2  1
         VC12-6   1  3  1
         VC12-7   2  3  1
         VC12-8   3  3  1
         VC12-9   1  4  1
         VC12-10  2  4  1
         VC12-11  3  4  1
         VC12-12  1  5  1
         VC12-13  2  5  1
         VC12-14  3  5  1
         VC12-15  1  6  1
         VC12-16  2  6  1
         VC12-17  3  6  1
         VC12-18  1  7  1
         VC12-19  2  7  1
         VC12-20  3  7  1
         VC12-21  1  1  2
         VC12-22  2  1  2
         VC12-23  3  1  2
         VC12-24  1  2  2
         VC12-25  2  2  2
         VC12-26  3  2  2
         VC12-27  1  3  2
         VC12-28  2  3  2
         VC12-29  3  3  2
         VC12-30  1  4  2
         VC12-31  2  4  2
         VC12-32  3  4  2
         VC12-33  1  5  2
         VC12-34  2  5  2
         VC12-35  3  5  2
         VC12-36  1  6  2
         VC12-37  2  6  2
         VC12-38  3  6  2
         VC12-39  1  7  2
         VC12-40  2  7  2
         VC12-41  3  7  2
         VC12-42  1  1  3
         VC12-43  2  1  3
         VC12-44  3  1  3
         VC12-45  1  2  3
         VC12-46  2  2  3
         VC12-47  3  2  3
         VC12-48  1  3  3
         VC12-49  2  3  3
         VC12-50  3  3  3
         VC12-51  1  4  3
         VC12-52  2  4  3
         VC12-53  3  4  3
         VC12-54  1  5  3
         VC12-55  2  5  3
         VC12-56  3  5  3
         VC12-57  1  6  3
         VC12-58  2  6  3
         VC12-59  3  6  3
         VC12-60  1  7  3
         VC12-61  2  7  3
         VC12-62  3  7  3

END


'''


    exscpAll = '''exscp:name=all;


SEMIPERMANENT CONNECTION DATA

NAME                      CSTATE   DISTC   MISC        NUMCH
LVIV-1                    RES      0                   3


SIDE1                    SSTATE   ATT  ES         MISCS
DEV=C7ST2C-1             RES        1
DEV=C7ST2C-2             RES
DEV=C7ST2C-3             RES

CH16                     CH24SYSTEM
YES                      NO

SIDE2                    SSTATE   ATT  ES         MISCS
DEV=C7ST2C-5             RES        1
DEV=C7ST2C-6             RES
DEV=C7ST2C-7             RES

CH16                     CH24SYSTEM
NO                       NO

NAME                      CSTATE   DISTC   MISC        NUMCH
SIM-SLC-0                 ACT      0                   1


SIDE1                    SSTATE   ATT  ES         MISCS
DEV=C7ST2C-0             ACT

SIDE2                    SSTATE   ATT  ES         MISCS
DEV=RALT2-1              ACT

END
'''

    tightPrintout = '''
SOME TIGHT PRINTOUT

PARAM1 PARAM2 PARAM3
V11      V12  V13  
V111111V122222V13
END
'''

    s7mspAll = """s7msp:sp=all,ssn=all;

SS7 SCCP MATED SUBSYSTEM DATA

SP           SSN      MSP          MSSN      MLSS
5-5-5          7      6-6-6         255
5-5-5          8      7-7-7           2
8-8-8          2                                9
6-6-6        255      5-5-5           7
7-7-7          2      5-5-5           8
END"""

    c7lpp = '''C7LPP:PARMG=0;
CCITT7 SIGNALLING LINK PARAMETER GROUPS

PARMG         0       1       2       3       4       5       6       7
T1S          49      49      49      49
T2S         100     100     100     100
T3MS       1000    1000    1000    1000
T4EMS       500     500     500     500
T4NS          8       8       8       8
T5MS        100     100     100     100
T6S           3       3       3       3
T7MS       2000    2000    2000    2000
TIN           4       4       4       4
TIE           1       1       1       1
M             5       5       5       5
N            16      16      16      16
T            64      64      64      64
D           256     256     256     256
ERC       BASIC   BASIC   BASIC   BASIC
INHI        TCC     TCC     TCC     TCC
CDL1         NO              NO      NO
   CA                35
   CO                45
   CD                70
CDLOCT1
   CA              2368
   CO              3008
   CD              4608
CDL2         NO      NO      NO      NO
   CA
   CO
   CD
CDLOCT2
   CA
   CO
   CD
CDL3         NO      NO      NO      NO
   CA
   CO
   CD
CDLOCT3
   CA
   CO
   CD
MAXSIF      272     272     272     272
END'''

    rapcp = '''
RAPCP;
PARAMETER COLLECTION SURVEY

REF
BSC136

REPMODE   INT
DELTA     5

END
'''

    exedpAll = '''EXEDP:EMG=ALL,EM=ALL;
EMGEM SOFTWARE UNIT AND EQUIPMENT DATA

EMG
OSBY4

EM
 0

SUNAME   SUID                            EQM                    SUP
EMGFDR   1402/CAA 117 054/1N    R3B01                           H'0012
RITSR    1946/CAA 117 1110/B07D R2A01                           H'00CD
TWR      2/CAA 117 058/1 E      R1A01    TW-0                   H'000C

EM
 1

SUNAME   SUID                            EQM                    SUP
EMGFDR   1402/CAA 117 054/1N    R3B01                           H'0012
RITSR    1946/CAA 117 1110/B07D R2A01                           H'00CD
TWR      2/CAA 117 058/1 E      R1A01    TW-7                   H'000C

EMG
OSBY

EM
NONE

EMG
OSBY2

EM
 0

SUNAME   SUID                            EQM                    SUP
EIEX1R   9000/CAA 203 58        R2B01                           H'0004

EM
11

SUNAME   SUID                            EQM                    SUP
NONE
END'''


    ntstp1 = '''
NTSTP:SNT=ALL;
SWITCHING NETWORK TERMINAL STATE

SNT                SUBSNT  STATE     BLS LST              FCODE
ETM2-0                     PBLOC     SBL
                   0       BLOC      MBL
                   1       WO
                   2       BLOC      MBL
                   3       BLOC      CBL
                   4       WO
ETM2-2                     BLOC      MBL
                   0       BLOC      MBL
ETM2-8                     WO
                   0       WO
ETM2-12                    TRAFBLOC  SBL
                   0       WO
                   1       BLOC      MBL

SNT                STATE       BLS   LST              FCODE
RTPGS-0            BLOC        MBL
RTPGS-1            BLOC        ABL
RTPGS-2            WO
RTSNT34-5          BLOC        MBL
RTSNT34-6          WO
RTAGWS-1           WO
RTAGWS-2           BLOC        CBL

END
'''

    rlsrp1 = '''
RLSRP:CELL=ALL;
CELL SYSTEM INFORMATION RAT PRIORITY DATA

CELL     PRIOCR  BCAST    FREE  REQ
112C202  OFF

RATPRIO  MEASTHR  PRIOTHR  HPRIO  TRES
         15        0       0      0

FDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU


EARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINE


TDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU


CELL     PRIOCR  BCAST    FREE  REQ
071C169  ON      NO        0    NA

RATPRIO  MEASTHR  PRIOTHR  HPRIO  TRES
1        16        2       3      4

FDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU
 3013               9         9         0
 3014       3       9         9         0
 3015       3       9         9         0

EARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINE
 1575            22        22         0
 3013   5        22        22         0

TDDARFCN  RATPRIO  HPRIOTHR  LPRIOTHR  QRXLEVMINU
 1575              22        22         0
 3013     5        22        22         0
END
'''

    exscpAll = '''
exscp:name=all;


SEMIPERMANENT CONNECTION DATA

NAME                      CSTATE   DISTC   MISC        NUMCH
LVIV-1                    RES      0                   3


 SIDE                     SSTATE   ATT  ES         MISCS
 DEV=C7ST2C-1             RES        1
 DEV=C7ST2C-2             RES
 DEV=C7ST2C-3             RES

 CH16                     CH24SYSTEM
 YES                      NO

 SIDE                     SSTATE   ATT  ES         MISCS
 DEV=C7ST2C-5             RES        1
 DEV=C7ST2C-6             RES
 DEV=C7ST2C-7             RES

 CH16                     CH24SYSTEM
 NO                       NO

 CONNID     DDINB                 REMNB
   1323      9874                   6589

NAME                      CSTATE   DISTC   MISC        NUMCH
SIM-SLC-0                 ACT      0                   1


 SIDE                     SSTATE   ATT  ES         MISCS
 DEV=C7ST2C-0             ACT

 SIDE                     SSTATE   ATT  ES         MISCS
 DEV=RALT2-1              ACT

END

'''

    rlslpAll = '''
RLSLP:CELL=ALL;
CELL SUPERVISION OF LOGICAL CHANNEL AVAILABILITY DATA

CELL
112C202

ACTIVE     CHTYPE                      LVA    ACL   NCH  NUMINT
YES        BTSPSSDCCH                     1   A3       0
           BTSPSTCH                       1   A3       0
           BTSPSTCHBPC                    1   A3       0
           PSSDCCH                        1   A3       0
           PSTCH                          1   A3       0
           PSTCHBPC                       1   A3       0

CELL       SCTYPE
112C202

ACTIVE     CHTYPE       CHRATE   SPV   LVA    ACL   NCH  NUMINT
YES        BCCH                           1   A1       0    40
           ECBCCH                         0   A3       0
           SDCCH                          1   A2       0
           TCH          FR       1        5   A3       0
           TCH          FR       2        0   A3       0
           TCH          FR       3        0   A3       0
           TCH          FR       5        0   A3       0    45
           TCH          HR       1        0   A3       0
           TCH          HR       3        0   A3       0
           TCHBPC                         1   A3       0
           CBCH                           1   A1       0

CELL
111C201

ACTIVE     CHTYPE                      LVA    ACL   NCH  NUMINT
YES        BTSPSSDCCH                     1   A3       0
           BTSPSTCH                       1   A3       0
           BTSPSTCHBPC                    1   A3       0
           PSSDCCH                        1   A3       0
           PSTCH                          1   A3       0
           PSTCHBPC                       1   A3       0

CELL       SCTYPE
111C201

ACTIVE     CHTYPE       CHRATE   SPV   LVA    ACL   NCH  NUMINT
YES        BCCH                           1   A1       0
           ECBCCH                         0   A3       0
           SDCCH                          1   A2       0
           TCH          FR       1        5   A3       0
           TCH          FR       2        0   A3       0
           TCH          FR       3        0   A3       0
           TCH          FR       5        0   A3       0
           TCH          HR       1        0   A3       0
           TCH          HR       3        0   A3       0
           TCHBPC                         1   A3       0
           CBCH                           1   A1       0
END
'''
    
    ihrhpAll = '''
ROUTE HANDLING

NVIF
ETHA-HLRFE_SIG_SP2

VID       IP              F        SUBNET              VER
1533      10.82.169.29             10.82.169.28/30     V4
          192.168.2.202   AUT      192.168.2.0/24      V4
          10.82.169.129            10.82.169.128/30    V4
          10.82.169.9              10.82.169.8/30      V4

DEFGW                                    PREF
192.168.2.1                              2

SOURCE          F                        PREF GW
10.82.169.129   f1                       6    192.168.2.111
10.82.169.129                            4    192.168.2.211
10.82.169.9                              7    192.168.2.111
10.82.169.9                              5    192.168.2.211

DEST                                     NETMASK
150.160.170.180                          255.255.255.255

GW                                       PREF SOURCE          F
192.168.2.100                            3    10.82.169.9     f2
192.168.2.200                            2    10.82.169.9
192.168.2.100                            3    10.82.169.129
192.168.2.200                            2    10.82.169.129

DEST                                     NETMASK
150.160.170.185                          255.255.255.255

GW                                       PREF SOURCE          F
192.168.2.100                            3    10.82.169.9
192.168.2.200                            2    10.82.169.9
192.168.2.100                            3    10.82.169.129
192.168.2.200                            2    10.82.169.129

DEST                                     NETMASK
124.124.125.221                          255.255.255.255

GW                                       PREF SOURCE          F
192.168.2.135                            7
192.168.2.13                             5

DEST                                     NETMASK
124.124.125.229                          255.255.255.255

GW                                       PREF SOURCE          F
192.168.2.137                            3
192.168.2.17                             1


NVIF
ETHB-HLRFE_SIG_SP2

VID       IP              F        SUBNET              VER
1533

DEFGW                                    PREF
192.168.2.129                            1

END

'''

    DBTSP_LMCONTRPARS = '''
DBTSP:TAB=LMCONTRPARS;
DATABASE TABLE

BLOCK   TAB             TABLE                           WRAPPED
LMCLI   LMCONTRPARS                                     NO

NAME            SETNAME         CNTRLMD VALUE STATUS  FROMSVR UPDREQ
ABISIP          CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
ACAISGRET       CME20BSCF       NORMAL      0 UNAVAIL FALSE   FALSE
ACAISGTMA       CME20BSCF       NORMAL      0 UNAVAIL FALSE   FALSE
ACCSTMA         CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
AMR             CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
AMRHR           CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
AMRWB           CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
AOIP            CME20BSCF       NORMAL  65535 AVAIL   FALSE   FALSE
AUTOFLP         CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
AUTOIRCT        CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
BTSPS           CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
CRESLTE         CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
CRESTDSCDMA     CME20BSCF       NORMAL      0 UNAVAIL FALSE   FALSE
CSCELLPAGE      CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
DCDL            CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
DTM             CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
EFTA            CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
EGPRS2ABPCLIMIT CME20BSCF       NORMAL  32760 AVAIL   FALSE   FALSE
EGPRSBPCLIMIT   CME20BSCF       NORMAL  32760 AVAIL   FALSE   FALSE
EPU             CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
FASTRETTDD      CME20BSCF       NORMAL      0 UNAVAIL FALSE   FALSE
FASTRETURNLTE   CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
IPM             CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
IURG            CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
LTEGSMNACC      CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
MCNSUPPORT      CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
MCTRPWR40       CME20BSCF       NORMAL   4095 AVAIL   FALSE   FALSE
MCTRPWR60       CME20BSCF       NORMAL   4095 AVAIL   FALSE   FALSE
MCTRPWR80       CME20BSCF       NORMAL   4095 AVAIL   FALSE   FALSE
MCTRTRX         CME20BSCF       NORMAL   4095 AVAIL   FALSE   FALSE
MIXEDMODERADIO  CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
PSCELLPAGE      CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
PSDLPC          CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
REDLAT          CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
RPWRHO          CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
RRUSCASCADE     CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
SCRAMBLESI      CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
SMSCBADVANCED   CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
SPIDPRIO        CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
VAMOSADVANCED   CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
M0001LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0026LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0047LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0048LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0056LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0068LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0069LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0079LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0085LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0090LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0091LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0099LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0110LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0114LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0117LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0122LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0126LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0139LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0145LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0146LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0173LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0174LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0187LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0189LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0191LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0196LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0202LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0203LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0204LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0206LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0212LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0213LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0217LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0221LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0229LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0231LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0232LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0233LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0234LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0239LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0242LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0244LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0249LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0251LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0252LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0254LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0256LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0257LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0260LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0262LIC        CME20BSCMAF     NORMAL      1 AVAIL   FALSE   FALSE
M0266LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0278LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0282LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0285LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0286LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0289LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0290LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0291LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0293LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0301LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0304LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0305LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0309LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0314LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0317LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0318LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0323LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0324LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0325LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0326LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0328LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0331LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0333LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0334LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0335LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0336LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0338LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0340LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0344LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0345LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0346LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0352LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0355LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0361LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0366LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0368LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0369LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
M0370LIC        CME20BSCMAF     NORMAL      0 UNAVAIL FALSE   FALSE
ABISIPCL        CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
AMRFRMAXTRAFFIC CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
AMRHRMAXTRAFFIC CME20BSCS       NORMAL  65520 AVAIL   FALSE   FALSE
AMRWBMAXTRAFFIC CME20BSCS       NORMAL  65535 AVAIL   FALSE   FALSE
ANR             CME20BSCS       NORMAL   2048 AVAIL   FALSE   FALSE
APSULPC         CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
AUTOFLPCL       CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
AUTOIRCTCL      CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
BCCHPS          CME20BSCS       NORMAL   2048 AVAIL   FALSE   FALSE
BTSPSCL         CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
BTSSOFTSYNC     CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
COMBINEDCELL    CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
CRESLTECL       CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
DCDLCL          CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
DTMCL           CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
EFTACL          CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
EPAS            CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
EVOETPORTS      CME20BSCS       NORMAL     64 AVAIL   FALSE   FALSE
FASTRETLTECL    CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
IPMCL           CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MCPAPS          CME20BSCS       NORMAL   2048 AVAIL   FALSE   FALSE
MCTRPWR100      CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MCTRPWR120      CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MAXNUMPDCH      CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
MAXNUMPDCH2     CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
MAXNUMPDCH3     CME20BSCS       NORMAL      0 UNAVAIL FALSE   FALSE
MAXNUMTRX       CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MAXNUMTRX2      CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MAXNUMTRX3      CME20BSCS       NORMAL      0 UNAVAIL FALSE   FALSE
MIXEDMODECL     CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MOCN            CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
NWSYNCHOCL      CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
PDECL           CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
REDLATCL        CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
VAMOSMAXTRAFFIC CME20BSCS       NORMAL  65520 AVAIL   FALSE   FALSE
A54MAXTRAFFIC   CME20BSCS       NORMAL  65520 AVAIL   FALSE   FALSE
MCTRPWR140      CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MCTRPWR160      CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
MULTISECTCL     CME20BSCS       NORMAL   4095 AVAIL   FALSE   FALSE
AHO             CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE
QOSAC           CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
ECGSM           CME20BSCS       NORMAL   2048 AVAIL   FALSE   FALSE
ECGSMBUCKET     CME20BSCS       NORMAL  65535 AVAIL   FALSE   FALSE
EDRX            CME20BSCS       NORMAL   2048 AVAIL   FALSE   FALSE
EDRXBUCKET      CME20BSCS       NORMAL  65535 AVAIL   FALSE   FALSE
QOSACBUCKET     CME20BSCS       NORMAL  65535 AVAIL   FALSE   FALSE
GSMRANRELLIC    CME20BSCF       NORMAL      1 AVAIL   FALSE   FALSE
QTA             CME20BSCS       NORMAL  32760 AVAIL   FALSE   FALSE

END
'''
#    prettyPrint(MMLparser().parsePrintouts(rlsvpALL))

#    prettyPrint(MMLparser(objHierarchy = {'SCGR':        ['SC']}).parsePrintouts(rrsspAll))
#    prettyPrint(MMLparser().parsePrintouts(rrsspAll))
    
#    prettyPrint(MMLparser(objHierarchy={'RP': ['SUNAME']}).parsePrintouts(exrupAll))
#    prettyPrint(MMLparser(objHierarchy={'RP': ['SUNAME']}).parsePrintouts(exrup))
#    prettyPrint(MMLparser().parsePrintouts(rrscpAll))
#    prettyPrint(MMLparser().parsePrintouts(rrntp))
#    prettyPrint(MMLparser().parsePrintouts(rlsvpAllBCCHPS))
#
#    prettyPrint(MMLparser().parsePrintouts(iougp))
#
#    prettyPrint(MMLparser().parsePrintouts(sastp))
#    prettyPrint(MMLparser().parsePrintouts(rlcrpCell))
#    prettyPrint(MMLparser().parsePrintouts(ntcopSnt))
#    
#    
#    prettyPrint(MMLparser().parsePrintouts(ihpgpAll))
#    prettyPrint(MMLparser().parsePrintouts(ihrtpHostAll))
#    prettyPrint(MMLparser().parsePrintouts(rlllpAll))
#    prettyPrint(MMLparser().parsePrintouts(rfimpAll))
#    prettyPrint(MMLparser().parsePrintouts(ihlpp))
#    prettyPrint(MMLparser().parsePrintouts(ntstpAll))
#    prettyPrint(MMLparser().parsePrintouts(trtspMp))
#    prettyPrint(MMLparser().parsePrintouts(syfsp))
#    prettyPrint(MMLparser().parsePrintouts(rxmopAllOTG))

#    prettyPrint(MMLparser().parsePrintouts(ntstpAll + '\n' + trtspMp + '\n' + syfsp))
#    prettyPrint(MMLparser().parsePrintouts(test1))
#    prettyPrint(MMLparser().parsePrintouts(ntcopAll))
#    prettyPrint(MMLparser().parsePrintouts(dbtspRPSRPBSPOS))
#    prettyPrint(MMLparser(objHierarchy={'SNT': ['SNTP', 'DIP', 'SDIP']}).parsePrintouts(ntcopEvo8200))
#    prettyPrint(MMLparser().parsePrintouts(c7sdpAll))


#    prettyPrint(MMLparser(objHierarchy={'ID1': ['SUB2', 'SUB22']}).parsePrintouts(test3Level))

#    res = MMLparser(objHierarchy={'ID1': ['SUB2', 'SUB22']}).parsePrintouts(test3Level)
#    
#    for obj in res:
#        for SUB22vals in obj['SUB22']:
#            for SUB22 in SUB22vals:
#                print 'SUB22:', SUB22
#                
#                # below pop() used to avoid dirty games with indexes ;)
#                print 'SUBPARA221:', obj['SUBPARA221'].pop(0)
#                print 'SUBPARA222:', obj['SUBPARA222'].pop(0)
#                print


#    prettyPrint(MMLparser().parsePrintouts(ihrsp))
#    prettyPrint(MMLparser().parsePrintouts(rfsdp))
#    prettyPrint(MMLparser(objHierarchy={'CELL': ['CHGR']}).parsePrintouts(rlbdpAll))
#    prettyPrint(MMLparser().parsePrintouts(dbtsp1))
#    prettyPrint(MMLparser(objHierarchy={'BLOCK': ['NAME']}).parsePrintouts(dbtsp2))
#    prettyPrint(MMLparser().parsePrintouts(rlmfpAll))
#    prettyPrint(MMLparser().parsePrintouts(rxmopTgs))
#    prettyPrint(MMLparser(objHierarchy={'CELL': ['SCTYPE']}).parsePrintouts(rllopAll))

#    prettyPrint(MMLparser(objHierarchy={'ID1': ['SUB2', 'SUB22'], 'CELL': ['SCTYPE']}).parsePrintouts(rllopAll + '\n' + test3Level))
#    prettyPrint(MMLparser().parsePrintouts(rxmop))
#    prettyPrint(MMLparser(objIds=['CELL']).parsePrintouts(rlsrpAll))
#    prettyPrint(MMLparser(objHierarchy={'CELL': ['CHGR']}).parsePrintouts(testStoreAsListofLists))
#    prettyPrint(MMLparser(objHierarchy={'CELL': ['LISTTYPE']}).parsePrintouts(rlumpAll))
#    prettyPrint(MMLparser(valDelimiters=None).parsePrintouts(rlmbpAll))
#    prettyPrint(MMLparser(horizParams=['HORIZPARAM1:', 'HORIZPARAM2:']).parsePrintouts(testHorizontal))
#    prettyPrint(MMLparser().parsePrintouts(testJustify))
#    prettyPrint(MMLparser(objIds = ['SUNAME'], valDelimiters = None).parsePrintouts(laeipAll))
#    prettyPrint(MMLparser().parsePrintouts(nsdap2))
#    prettyPrint(MMLparser().parsePrintouts(exrppAll))
#    prettyPrint(MMLparser().parsePrintouts(rlvgpAll))
#    prettyPrint(MMLparser().parsePrintouts(rlnrpAll))
#    prettyPrint(MMLparser().parsePrintouts(testNone))
#    prettyPrint(MMLparser(objHierarchy={'SDIP': ['LAYER']}, valDelimiters=None).parsePrintouts(tptipAll))
#    prettyPrint(MMLparser(objIds=['NAME', 'SIDE1', 'SIDE2']).parsePrintouts(exscpAll))
#    prettyPrint(MMLparser().parsePrintouts(tightPrintout))
#    prettyPrint(MMLparser().parsePrintouts(s7mspAll))
#    prettyPrint(MMLparser().parsePrintouts(c7lpp))
#    prettyPrint(MMLparser(objIds=['REF'], objHierarchy={'REF': ['REPMODE']}).parsePrintouts(rapcp))
#    prettyPrint(MMLparser(objHierarchy = {'EM': ['SUID']}, valDelimiters="").parsePrintouts(exedpAll))
#    prettyPrint(MMLparser(objHierarchy = {'EMG': ['EM', 'SUNAME']}, valDelimiters="").parsePrintouts(exedpAll))
#    prettyPrint(MMLparser(objHierarchy={'SNT': ['SUBSNT']}).parsePrintouts(ntstp1))
#    prettyPrint(MMLparser(objHierarchy = {'CELL': ['FDDARFCN', 'EARFCN', 'TDDARFCN']}).parsePrintouts(rlsrp1))
#    prettyPrint(MMLparser(objHierarchy = {'NAME': ['SIDE']}).parsePrintouts(exscpAll))
#    prettyPrint(MMLparser(objHierarchy = {'CELL': ['CHTYPE']}).parsePrintouts(rlslpAll))
#    prettyPrint(MMLparser(objHierarchy = {'NVIF': ['DEST']}).parsePrintouts(ihrhpAll))
    prettyPrint(MMLparser().parsePrintouts(DBTSP_LMCONTRPARS))
