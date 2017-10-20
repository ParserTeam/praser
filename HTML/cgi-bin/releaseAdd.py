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
    file = open('.\config\\versions.txt','a')
    file.write('\n'+fadd)
    file.close()
    file = open('.\config\\versions.txt','r')
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
    fin = open('.\config\\versions.txt',)
    text = fin.read()
    lines = text.split("\n")
    fin.close()
    fout = open('.\config\\versions.txt', "w")
    lines.remove(fdel)
    fout.write("\n".join(lines))
    fout.close()
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
    file = open('.\config\\versions.txt', 'r')
    for line in file:
        print line +  ';'
    file.close()
    '''</p>'''
    print '''
    </body>
    </html>
'''
