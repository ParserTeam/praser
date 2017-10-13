import cgi
from tkFileDialog import askopenfile
from Tkinter import Tk, Button, Label, Toplevel



def get_input_inf(): # it take oll inut infornation from web to server (if it is upload file - read file using withdraw Class, else take take value from text area)
    # Get data from fields
    form = cgi.FieldStorage()

    if not form.list:
        root = Tk()
        root.withdraw()
        print_file = askopenfile("r")
        if print_file:
            return print_file.read()
        return "Error"
    elif form.list[0].name == "comment":
        return form.getvalue("comment")
    return "No input data"


def output_inf(output): #use it to print dynamic table with the result information after parsing
    print "Content-type:text/html\r\n\r\n"
    if type(output) == str:
        print "<p>" + output + "</p>"
    else:
        a = output
        # a = {'rrscp.xml': [{'SC': '0', 'REASON': {'b27': 'Not activated in RP unit'}, 'SCGR': ['20']}, {'SC': '1', 'REASON': {'b27': 'Not activated in RP unit'}, 'SCGR': ['20']}, {'SC': '0', 'REASON': {'b27': 'Not activated in RP unit'}, 'SCGR': ['21']}]}
        print a
        if len(a) != 0:
            print '''
                <link rel="stylesheet" type="text/css" href="style.css">
                <link rel='stylesheet prefetch' href='http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css'>
                <link rel='stylesheet prefetch' href='http://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.10.0/bootstrap-table.min.css'>
                <link rel='stylesheet prefetch' href='http://rawgit.com/vitalets/x-editable/master/dist/bootstrap3-editable/css/bootstrap-editable.css'>
                <div class="container">
                 <table class="table table-bordered">
            '''
            for i in a:
                g = ""
                print '''
                                    <tr>
                                            <th colspan="4" ></th>
                                    </tr>
                                '''
                print '''
                    <tr>
                        <th colspan="4"style="text-align:  center;" >''' + i[:i.find(".")].upper() + '''</th>
                    </tr>
                '''
                for j in a.get(i):
                    # print '''
                    #                         <tr>
                    #                                 <th colspan="4" ></th>
                    #                         </tr>
                    #                     '''
                    b = j
                    for z in b:
                        if type(b.get(z)) == list:
                            for h in b.get(z):
                                if str(h) != g:
                                    print '''
                                        <tr style="background: rgba(51,68,183,0.7)">
                                          <th>''' + z + '''</th>
                                          <th colspan="3" >''' + str(h) + '''</th>
                                        </tr>
                                    '''

                                g = str(h)
                    for z in b:

                        if type(b.get(z)) != dict and type(b.get(z)) != list:
                            print '''
                                <tr class="bg-primary">
                                  <th>''' + z + '''</th>
                                  <th colspan="3" >''' + b.get(z) + '''</th>
                                </tr>
                            '''

                    for z in b:
                        if type(b.get(z)) == dict:
                            if len(b.get(z)) != 0:
                                print '''
                                    <tr style="background: rgba(154, 206, 235, 0.7) ">
                                      <th>''' + z + '''</th>
                                      <th colspan="3" >VALUES:</th>
                                    </tr>
                                '''
                                for y in b.get(z):
                                    print '''
                                        <tr class="bg-success ">
                                          <th>''' + y + '''</th>
                                          <th colspan="3" >''' + b.get(z).get(y) + '''</th>
                                        </tr>
                                    '''
            print '''
                        </table>
                </div>
                    '''


class DialogWindow: # use it to upload file from local directory after press button Upload
    window = None
    question = "This text is OK?"
    return_value = None
    title = None

    def __init__(self, title, question):
        self.question = question
        self.title = title

    def _on_button_click(self, event):
        self.return_value = event.widget._name
        self.window.destroy()

    def get_answer(self, text, button_list):
        self.window = Tk()
        self.window.title(self.title)
        self.window.minsize(width=100, height=100)
        label_text = "{} \n\n {}".format(self.question, text)
        Label(self.window, text=label_text, anchor="w", justify="left").pack(fill="both")
        for button_name in button_list:
            button = Button(self.window, text=button_name, name=button_name.replace(".", "|dot|"))
            button.pack(fill="both")
            button.bind("<Button-1>", self._on_button_click)
        self.window.focus_set()
        self.window.grab_set()
        self.window.wait_window()
        print self.return_value.replace("|dot|", ".") if self.return_value else None

