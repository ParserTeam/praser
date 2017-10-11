import cgi
from tkFileDialog import askopenfile
# from Controler import Controller

# from XmlModule import ConfigModule



# test = ConfigModule()

# Create instance of FieldStorage



def get_input_inf():
    # Get data from fields
    form = cgi.FieldStorage()

    if not form.list:
        print_file = askopenfile("r")
        return print_file.read()
    elif form.list[0].name == "comment":
        return form.getvalue("comment")
    return "No input data"



# controller = Controller()
# text = controller.check_text(get_input_inf())


# output = ['new inf']


def output_inf(output):
    print "Content-type:text/html\r\n\r\n"
    if type(output) == str:
        print "<p>" + output + "</p>"
    else:
        a = output
        print type(a)

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
                    b = j
                    print '''
                        <tr>
                                <th colspan="4" ></th>
                        </tr>
                    '''
                    for z in b:
                        if type(b.get(z)) != dict:
                            print '''
                                <tr class="bg-primary">
                                  <th>''' + z + ''' -''' + '''</th>
                                  <th colspan="3" >''' + b.get(z) + ''' ;''' + '''</th>
                                </tr>
                            '''

                    for z in b:
                        if type(b.get(z)) == dict:
                            if len(b.get(z)) != 0:
                                print '''
                                    <tr style="background: rgba(154, 206, 235, 0.7) ">
                                      <th>''' + z + ''' :''' + '''</th>
                                      <th colspan="3" >ERRORS:</th>
                                    </tr>
                                '''
                                for y in b.get(z):
                                    print '''
                                        <tr class="bg-success ">
                                          <th>''' + y + ''' -''' + '''</th>
                                          <th colspan="3" >''' + b.get(z).get(y) + ''' ;''' + '''</th>
                                        </tr>
                                    '''
                            # else:
                            #     print'''
                            #         <tr class="bg-success ">
                            #           <th>''' + z + ''' -''' + '''</th>
                            #           <th colspan="3" >OK;</th>
                            #         </tr>
                            #     '''
            print '''
                        </table>
                </div>
                    '''


def select_version(L, Text):
    """:return L(random object)"""
    import random
    secure_random = random.SystemRandom()
    rand = secure_random.choice(L)
    return [rand]


