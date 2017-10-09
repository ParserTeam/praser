You must write a .xml file with the following structure:
<?xml version="1.0" encoding="UTF-8"?>
<root limiter=here you need to specify a table header (start) and mandatory keywords.>
    <HEDER>specify the decryption of the name of the printout</HEDER>
    <KEYS>specify the name of the column in which to find and decrypt the error</KEYS>
    <NAME_KEY>The abbreviation for the object names for which we will perform the printout</NAME_KEY>
    <ACTIVE_KEYS limiter=""> - Inside this tag, all the keys specified in the <KEYS> tag with the error encoding, are taken from the documentation in the following form (for each key separately):
        <The name of the first key specified in the key <KEYS> type=System of calculation in which specified value of this key in the printout norm_val=key value indicating no error>
            <The value of the 1st bit specified in the documentation bit=Lighted Bit Number (1)>Description of the error taken from the documentation</The bit value specified in the documentation>
            .
            .
            .
            <The n-th bit specified in the documentation bit=Lighted Bit Number (n)>Description of the error taken from the documentation</The bit value specified in the documentation>
        </The name of the first key specified in the <KEYS> tag>
    </ACTIVE_KEYS>
    <PRINT_KEYS>you must specify an additional parameter (specified in a separate table of the print out, that is separated by an empty string from the main table where the key values are specified) that must be displayed on the screen together with the error, if any. Otherwise, this tag remains empty
    </PRINT_KEYS>
</root>

This file must be placed in the "config" directory of the given project.