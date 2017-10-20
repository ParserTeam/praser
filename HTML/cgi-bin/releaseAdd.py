import cgi, cgitb
from tkFileDialog import askopenfile
from Tkinter import Tk, Button, Label
import os

form = cgi.FieldStorage()
fadd= form.getvalue('txt')
fdel  = form.getvalue('txtdel')


if fdel == None and fadd == None:
    file = open('.\config\\versions.txt', 'r')
    print '''
        <html>
        <head>
        <TITLE>PARSER</TITLE>
        <link rel="stylesheet" type="text/css" href="http://localhost:8000/style.css">
        </head>
        <body>
        <div id ="goback"><p>&nbsp</p><nav><a href="http://localhost:8000/">BACK TO PARSER</a></nav><p>&nbsp</p></div>
        <div>
        <P>&#8195;You typed any version of release.</P>
        <div>
        <p STYLE="color:blue">&#8195;RELEASES:</p> '''
    for line in file:
        print line + ';'
    file.close()
    print '''
        </body>
        </html>
        '''

if fadd != None:
    file = open('.\cgi-bin\\versions.txt','a')
    file.write('\n'+fadd)
    file.close()
    file = open('.\cgi-bin\\versions.txt','r')
    print '''
    <html>
    <head>
    <TITLE>PARSER</TITLE>
    <link rel="stylesheet" type="text/css" href="http://localhost:8000/style.css">
    </head>
    <body>
    <div id ="goback"><p>&nbsp</p><nav><a href="http://localhost:8000/">BACK TO PARSER</a></nav><p>&nbsp</p></div>
    <div>
    <P>&#8195;New version of release wos added successfully.</P>
    <div>
    <p STYLE="color:blue">&#8195;RELEASES: '''
    for line in file:
        print line +  ';'
    file.close()
    '''</p>'''
    print '''
    </body>
    </html>
        '''

if fdel != None:
    pattern = fdel
    fin = open('.\cgi-bin\\versions.txt',)
    fout = open('.\cgi-bin\\versions2.txt', "w")
    for line in fin.readlines():
        if not pattern in line:
            fout.write(line)
    fin.close()
    fout.close()
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'versions.txt')
    os.remove(path)
    os.rename('.\cgi-bin\\versions2.txt', '.\cgi-bin\\versions.txt')
    print '''
    <html>
    <head>
    <TITLE>PARSER</TITLE>
    <link rel="stylesheet" type="text/css" href="http://localhost:8000/style.css">
    </head>
    <body>
    <div id ="goback"><p>&nbsp</p><nav><a href="http://localhost:8000/">BACK TO PARSER</a></nav><p>&nbsp</p></div>
    <div>
    <P>&#8195;Version of release wos deleted successfully.</P>
    <div>
    <p STYLE="color:blue">&#8195;RELEASES: '''
    file = open('.\cgi-bin\\versions.txt', 'r')
    for line in file:
        print line +  ';'
    file.close()
    '''</p>'''
    print '''
    </body>
    </html>
'''
