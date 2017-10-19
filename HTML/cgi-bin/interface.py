import cgi
from tkFileDialog import askopenfile
from Tkinter import Tk, Button, Label


def get_input_inf(): # it take oll inut infornation from web to server (if it is upload file - read file using withdraw Class, else take take value from text area)
    # Get data from fields
    form = cgi.FieldStorage()

    if "text" not in form or "file" in form:
        root = Tk()
        root.withdraw()
        print_file = askopenfile("r")
        if print_file:
            return form.getvalue("version"), print_file.read()
        return "Error"
    else:
        return form.getvalue("version"), form.getvalue("text")


def get_versions():
    print "Content-type:text/html\r\n\r\n"
    versions_file = open("config/versions.txt")
    print "<p>"
    for line in versions_file.readlines():
        default = 'checked="checked"' if line == "A58" else ""
        print '<input type="radio" name="version" {} value="{}"> {} '.format(default, line, line)
    print "</p>"


def output_inf(output): #use it to print dynamic table with the result information after parsing
    mainId = 0
    valuesId = 0
    mainDict = {}
    print "Content-type:text/html\r\n\r\n"
    if type(output) == str:
        print "<p>" + output + "</p>"
    else:
        a = output
        # a = {'rrscp.xml': [{'SC': '0', 'REASON': {'b27': 'Not activated in RP unit'}, 'SCGR': ['20']}, {'SC': '1', 'REASON': {'b27': 'Not activated in RP unit'}, 'SCGR': ['20']}, {'SC': '0', 'REASON': {'b27': 'Not activated in RP unit'}, 'SCGR': ['21']}]}
        if len(a) != 0:
            print '''
                <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
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
                    if len(g) == 0:
                        print '''
                                                <tr>
                                                        <th colspan="4" ></th>
                                                </tr>
                                            '''
                    b = j
                    for z in b:
                        if type(b.get(z)) == list:
                            for h in b.get(z):
                                if str(h) != g:
                                    print '''
                                                            <tr>
                                                                    <th colspan="4" ></th>
                                                            </tr>
                                                        '''
                                    print '''
                                        <tr style="background: rgba(51,68,183,0.7)">
                                          <th style ="width:192;">''' + z + '''</th>
                                          <th colspan="3" >''' + str(h) + '''</th>
                                        </tr>
                                    '''

                                g = str(h)
                    for z in b:

                        if type(b.get(z)) != dict and type(b.get(z)) != list:
                            print '''
                                <tr class="bg-primary">
                                  <th style ="width:192;">''' + z + '''</th>
                                  <th colspan="3" >''' + b.get(z) + '''</th>
                                </tr>
                            '''

                    for z in b:
                        if type(b.get(z)) == dict:
                            if len(b.get(z)) != 0:
                                mainId += 1
                                print '''
                                    <tr style="background: rgba(154, 206, 235, 0.7) " id="''' + str(mainId) +'''">
                                      <th style ="width:192;">''' + z + '''</th>
                                      <th colspan="3" style ="position:relative;">VALUES:<a href="#" id="moreless''' +str(mainId)+'''" style ="position:absolute; left: 90%;"> Less inf.</a></th>
                                    </tr>
                                '''

                                for y in b.get(z):
                                    valuesId += 1
                                    tempValue = str(mainId) + "-" + str(valuesId)
                                    tempDict = {mainId:tempValue}
                                    mainDict.update(tempDict)
                                    print '''
                                        <tr class="bg-success " id="''' + str(mainId) + "-" + str(valuesId) +'''">
                                          <th style ="width:192;">''' + y + '''</th>
                                          <th colspan="3" >''' + b.get(z).get(y) + '''</th>
                                        </tr>
                                    '''

                                valuesId = 0
            for mainCount in range(1, mainId+1):
                print '''
                                    <script language="javascript">
                                    $(document).ready(function(){
                                    '''
                # for y in range(mainId+1): #undock to hide for defoult
                    # print '''
                    #     $("#''' + str(x) + "-" + str(y) + '''").hide();
                    #     '''
                print '''
                        $("#moreless''' + str(mainCount) + '''").click(function(e''' + str(mainCount) + "_" + str(mainCount) + ''') {
                '''
                for valueCount in range(1, int(mainDict.get(mainCount)[mainDict.get(mainCount).find("-")+1:])+1):
                    print '''
                                var allother''' + str(mainCount) + "_" + str(valueCount) + ''' = $("#''' + str(mainCount) + "-" + str(valueCount) + '''");
                                $(this).text(allother''' + str(mainCount) + "_" + str(valueCount) + '''.is(":hidden") ? "Less inf." : "More inf.");    
                                allother''' + str(mainCount) + "_" + str(valueCount) + '''.slideToggle();
                                
                                '''   #hidden --> visible
                print '''
                
                                e''' + str(mainCount) + "_" + str(mainCount) + '''.stopImmediatePropagation();
                                return false;
                            });
                        });
                        </script>
                        '''
            print '''
                        </table>
                </div>
                 <a href="#top" CLASS="toTop"> UP </a >
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

if __name__ == "__main__":
    get_versions()
