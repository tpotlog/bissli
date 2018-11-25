import snack
class NoFormsInListException(Exception):
    '''
    The List which was given was an empty list of Forms
    '''
    def __init__(self):
        self.msg='Form list given is empty'
    def __str__(self):
        return self.msg

class NotAllFormsAreBaseForm(Exception):
    '''
    The List which was given was held some object which is not an instance of BaseForm
    '''
    def __init__(self,object,index):
        self.msg='Form list containe non BaseForm objects, object is %s ,index %s' %(str(object),str(index))
    def __str__(self):
        return self.msg

class NoWidgetsInWidgetsList(Exception):
    '''
    The List which was given was was empty
    '''
    def __init__(self,object,index):
        self.msg='Widget list is empty'
    def __str__(self):
        return self.msg


class BaseForm(object):
    '''
    This Class is the basic form calss which is actually a wrapper around
    snack.Form / snack.GridForm / snack.GridFormHelp

    Addtional arguments:

    Widgets         - A List/Tuple of a widgets to be used in this form

    '''

    def __init__(self,screen,name,frm=None,**kargs):

        self.frm=frm
        self.screen=screen
        self.name=name
        self.result=None
        self.init=False
        if not kargs.get('Widgets',None):
            self.Widgets=[]
        else:
            self.Widgets=kargs['Widgets']


    def next(self):
        '''
        The next method should return

        The next form to read from a list
        or
        1  , if we do not know which is the next Form but the form results were OK
        or
        0 , if the form results are not ok with us
        or
        -1 , which should be defined by use default (probably for backing in a wizrd)
        '''
        return 1

    def _pack(self):
        '''
        This function should pack all the Widgets into the form is is automaticlly called when using run

        Overrid this per specialized form
        '''
        if not len(self.Widgets):
               raise NoWidgetsInWidgetsList()

        c=1
        r=len(self.Widgets)
        self.frm=snack.GridForm(self.screen,self.name,c,r)
        for p in range(0,len(self.Widgets)):
               self.frm.add(self.Widgets[p],0,p)
        self.init=True

    def run(self):
        '''
        simply tun rhe sanck form run
        '''
        self._pack()
        self.result=self.frm.run()

    def runOnce(self):
        '''
        simply tun rhe sanck form runOnce
        '''
        self._pack()
        self.result=self.frm.runOnce()

    def getData(self):
        '''
        This option will go over all the Widgets in the form and return the values of each one
        '''
        return None


class FormFlow(object):
    '''
    Forms Flow is a calls which will hold a list of forms to be excuted

    The from flow can be in one of the following statuses:
    Init    - The module is in init mode which means no one called the __iter__ yet
    ExitOK  - The form flow ended ok without any problem
    ExitErr - The form flow eded with some form reporting error
    ExitIter- Something went wrong while terating over the forms probably one of the from in the list is not ,True/False/BaseForm
    OnGoing - The form flow is in OnGoing stat , meanning that current forms are running

    '''

    Init,ExitOK,ExitErr,ExitIter,OnGoing=range(0,5)



    def __init__(self,FormsList):
        '''
        FormsList is a list of forms to go over
        '''
        ###Do some sanity tests before going on##
        #a) List can not be empty
        if not len(FormsList):
            raise NoFormsInListException()
        #b) Does all the objects are instances of BaseForm
        for o in FormsList:
            if not isinstance(o,BaseForm):
                raise NotAllFormsAreBaseForm(o,FormsList.index(o))

        ##All is fine lets get to work###
        self.FormsList=FormsList
        self.current_form=FormsList[0]
        self.State=self.Init

    def __iter__(self):
        '''
        Just for the formalities define __iter__
        '''
        return self
        
    def StopIter(self):
        '''
        Stop the iteration , which actually mean raise StopIteration
        '''
        raise StopIteration

    def next(self):
        ###If we are in intializing mode then return the current###
        if self.State == self.Init:
            self.State=self.OnGoing
            return self.current_form

        ###We are not in initialize mode###
        Form_Next=self.current_form.next()
        if Form_Next == 0:
            self.State=self.ExitErr
            self.StopIter()
        elif Form_Next == 1:
            form_idx=self.FormsList.index(self.current_form)
            ###Are We at the end of the list###
            if form_idx == (len(self.FormsList) - 1):
                 self.State=self.ExitOK
                 self.StopIter()
            else:
                self.current_form=self.FormsList[form_idx+1]
        elif Form_Next == -1:
            form_idx=self.FormsList.index(self.current_form)
            ###Are We at the beginning of the list###
            if form_idx == 0:
                '''
                Do nothing if you are at the beginning of a list
                '''
                pass
            else:
                self.current_form=self.FormsList[form_idx-1]


        elif isinstance(Form_Next,BaseForm):
            '''
            If we have an instance of BaseForm we use it
            '''
            self.current_form=Form_Next
        else:
            # Theoretically this should be an exception, however
            # it is more convenient to exit the form in an orderly
            # fashion.
            self.State=self.ExitIter
            self.StopIter()

        return self.current_form



class MenuForm(BaseForm):
    '''
    This is a special form from the type of menu which is creating a menu.

    The menu should look something like this
    +---------------------------+
    |                           |
    |   1) <option 1>           |
    |   2) <option 2>           |
    |   .                       |
    |   .                       |
    |   .                       |
    |                           |
    |                           |
    |                           |
    |                           |
    |   +----+     +--------+   |
    |   | OK |     | Cancel |   |
    |   +----+     +--------+   |
    +---------------------------+


    Variables:
    ---------
    option          - A list of tupels/lists at the format of (<Displayed text>,<Returned value>) .
    screen          - The screen to be used by the snack form.
    title           - The Menu Title.
    height          - Menu list height (lines)
    width           - Menu list width  (chars/columns)
    ok_button       - A tuple/List at the format of (<Button Title>,<return value>)
    cancel_button   - A tuple/List at the format of (<Button Title>,<return value>)

    Addtional arguments:

    Buttons         - If the keyword Buttons is given, it is assumet to be a widget and added to the form insted of the Ok/Cancel Buttons


    '''
    def __init__(self,options,screen,title,height=5,width=20,ok_button=('Ok',1),cancel_button=('Cancel',0),**kargs):
        '''
        Initialize the menu and the BaseForm
        '''
        self.title=title
        self.SnackList=snack.Listbox(height=height,width=width)
        n=1
        for p in options:
             self.SnackList.append( "%d) %s"%(n,p[0]), p[1] )
             n+=1
        if kargs.get('Buttons',None):
            self.Buttons=kargs['Buttons']
        else:
            self.Buttons = snack.ButtonBar(screen, (ok_button,cancel_button))
        super(MenuForm,self).__init__(screen=screen,name=title,Widgets=[self.SnackList,self.Buttons],**kargs)
        ###Add Widgets to the Widgets list###

    def next(self):
        '''
        Test The Value of the pressed button, and return it's value if possiable
        '''
        x=self.Buttons.buttonPressed(self.result)
        if not self.result or x is None:
            # F12 was pressed
            return 1
        return x

    def getData(self):
        '''
        Return the current selection
        '''
        return self.SnackList.current()


class WizardMenuForm(MenuForm):
    '''
    This is a MenuForm just like MenuForm Class.
    How ever it is more suited to Wizards since it contains 3 buttons Back,Cancel,Next


    The menu should look something like this
    +---------------------------+
    |                           |
    |   1) <option 1>           |
    |   2) <option 2>           |
    |   .                       |
    |   .                       |
    |   .                       |
    |                           |
    |                           |
    |                           |
    |                           |
    | +----+  +--------+ +----+ |
    | |Back|  | Cancel | |Next| |
    | +----+  +--------+ +----+ |
    +---------------------------+


    Variables:
    ---------
    option          - A list of tupels/lists at the format of (<Displayed text>,<Returned value>) .
    screen          - The screen to be used by the sack form.
    title           - The Menu Title.
    height          - Menu list height (lines)
    width           - Menu list width  (chars/columns)
    '''

    def __init__(self,options,screen,title,height=5,width=20,**kargs):
            '''
            Initialize the class basiclly it is just
            '''
            self.Buttons = snack.ButtonBar(screen, (('Back',-1),('Cancel',0),('Next',1)))
            super(WizardMenuForm,self).__init__(options,screen,title,height,width,Buttons=self.Buttons)

class EntryForm(BaseForm):
    '''
    This Form is to be used for entry of values

    The form would look something like this

    +---------------------------+
    |                           |
    |   label1 ______           |
    |   label2 ______           |
    |   .                       |
    |   .                       |
    |   .                       |
    |                           |
    |                           |
    |                           |
    |                           |
    |   +----+     +--------+   |
    |   | OK |     | Cancel |   |
    |   +----+     +--------+   |
    +---------------------------+


    Variables:
    ---------
    screen          - The screen to be used by the sack form.
    Entries         - A list of Tupels/Lists ath the format of (<Entry label>,<Entry Text>)
    title           - The form Title.
    width           - The width of the entry
    ok_button       - A tuple/List at the format of (<Button Title>,<return value>)
    cancel_button   - A tuple/List at the format of (<Button Title>,<return value>)
    columns         - spread the entries across X colums

    Addtional arguments:

    Buttons         - If the keyword Buttons is given, it is assumet to be a widget and added to the form insted of the Ok/Cancel Buttons


    #TODO:
     The form does not handle scrolling, need to find a way to scroll the form
    '''


    def __init__(self,Entries,screen,title,columns=1,width=30,ok_button=('Ok',1),cancel_button=('Cancel',0),**kargs):
        '''
        Initialize the form
        '''
        self.width=width
        self.MsgBox=snack.TextboxReflowed(width,' ')
        self.Entries=Entries
        self.EntriesLen=len(Entries)
        self.columns=columns
        self.EntriesGrid=snack.Grid(columns *2,self.EntriesLen )
        self.Members={} # {<lable-text>:<entry-text-obj>,...}
        if kargs.get('Buttons',None):
           self.Buttons=kargs['Buttons']
        else:
           self.Buttons = snack.ButtonBar(screen, (ok_button,cancel_button))
        EntriesGrid=self.getEntriesGrid()
        super(EntryForm,self).__init__(screen,title,Widgets=[self.MsgBox,EntriesGrid,self.Buttons])

    def getEntriesGrid(self):
        '''
        This function will return the entries grid built from the Entries List considering the colums
        '''
        EntriesGrid=snack.Grid(self.columns *2,len(self.Entries))
        self.Members={}
        k=0  # acts as X
        z=-1 # acts as Y
        for i in range(0,len(self.Entries)):
            if i % self.columns == 0:
                z=z+1
                k=0
            L=snack.Label(text=str(self.Entries[i][0]))
            E=snack.Entry(width=self.width,text=str(self.Entries[i][1]))
            EntriesGrid.setField(L,k+i%self.columns,z,padding=(1,0,0,0)) #Set the label
            EntriesGrid.setField(E,k+1+i%self.columns,z,padding=(1,0,0,0)) #Set the entry
            self.Members[str(self.Entries[i][0])]=E
            k=k+1
        return EntriesGrid

    def addEntry(self,label,value=''):
        '''
        Add entry (if not already exists) to both the member dict ad as a label & entry to the form
        '''
        if not self.Members.has_key(label):
           self.Entries.append((label,value))
           E=self.getEntriesGrid()
           self.Widgets=[self.MsgBox,E,self.Buttons]

    def addMessage(self,message):
        '''
        Add a message at the top of the list
        '''
        self.MsgBox.setText(message)

    def next(self):
        '''
        Test The Value of the pressed button, and return it's value if possiable
        '''
        x=self.Buttons.buttonPressed(self.result)
        if not self.result or x is None:
            return 1
        return x

    def getData(self):
        '''
        Return all the values from the entries ath the format of a dictionary
        {
         label1:Entry1,
         label2:Entry2,
         .
         .
         labelN:EntryN
        }
        '''
        _members={}
        for M in self.Members:
            _members[M]=self.Members[M].value()
        return _members

class DynamicEntryForm(EntryForm):
    '''
    This class is an EntryFrom class type with addtional button added to allow adding field top the form
    The button label will be Add Entry , by clicking on it a popup window will appear and ask the user to
    add value, which will apear in the new form afre running again the run function of the EntryForm.

    The form will look like this

    +-----------------------------------+
    |                                   |
    |   label1 _____________________    |
    |   label2 _____________________    |
    |   .                               |
    |   .                               |
    |   .                               |
    |                                   |
    |                                   |
    |                                   |
    |                                   |
    |   +----+ +---------+ +--------+   |
    |   | OK | |Add Entry| | Cancel |   |
    |   +----+ +---------+ +--------+   |
    +-----------------------------------+


    Variables:
    ---------
    screen          - The screen to be used by the sack form.
    Entries         - A list of Tupels/Lists ath the format of (<Entry label>,<Entry Text>)
    title           - The form Title.
    width           - The width of the entry.
    columns         - spread the entries across X colums.
    ok_text         - The text label on the ok button.
    cancel_text     - The text label on the cancel button.
    add_entry_text  - The text label on the add entry button.


    #TODO:
    The form does not handle scrolling, need to find a way to scroll the form
    '''

    def __init__(self,screen,Entries,title,width=20,columns=1,ok_text='Ok',cancel_text='Cancel',add_entry_text='Add Entry',**kargs):

        if kargs.get('Buttons',None):
                  self._Buttons=kargs['Buttons']
        else:
            self._Buttons = snack.ButtonBar(screen, ((ok_text,1),(add_entry_text,3),(cancel_text,0)))

        super(DynamicEntryForm,self).__init__(Entries=Entries,screen=screen,title=title,columns=columns,width=width,Buttons=self._Buttons)

    def next(self):
        l=self.Buttons.buttonPressed(self.result)
        if l == 1 or l is None:
            return 1
        if l == 3:
            f=EntryForm(Entries=[('Add Entry','')],title='Add Entry',screen=self.screen)
            f.run()
            self.screen.popWindow()
            if f.next()==1:
                d=f.getData()['Add Entry']
                self.addEntry(label=d)
            return self
        return l

class WizardEntryForm(EntryForm):
    '''
    This is a MenuForm just like MenuForm Class.
    How ever it is more suited to Wizards since it contains 3 buttons Back,Cancel,Next


    The menu should look something like this
    +---------------------------+
    |                           |
    |   1) ____________         |
    |   2) ____________         |
    |   .                       |
    |   .                       |
    |   .                       |
    |                           |
    |                           |
    |                           |
    |                           |
    | +----+  +--------+ +----+ |
    | |Back|  | Cancel | |Next| |
    | +----+  +--------+ +----+ |
    +---------------------------+

    Variables:
    ---------
    screen          - The screen to be used by the sack form.
    Entries         - A list of Tupels/Lists ath the format of (<Entry label>,<Entry Text>)
    title           - The form Title.
    width           - The width of the entry
    ok_button       - A tuple/List at the format of (<Button Title>,<return value>)
    cancel_button   - A tuple/List at the format of (<Button Title>,<return value>)

    Addtional arguments:

    Buttons         - If the keyword Buttons is given, it is assumet to be a widget and added to the form insted of the Ok/Cancel Buttons

    '''
    def __init__(self,Entries,screen,title,columns=1,width=30,**kargs):
            '''
            Initialize the class basiclly it is just
            '''
            if kargs.get('Buttons',None):
                  self.Buttons=kargs['Buttons']
            else:
                self.Buttons = snack.ButtonBar(screen, (('Back',-1),('Cancel',0),('Next',1)))
            super(WizardEntryForm,self).__init__(Entries,screen,title,columns,width,Buttons=self.Buttons)

class DynamicWizardEntryForm(EntryForm):
    '''
    This is an Wizard Entry but with the option to dynamiclly add entries

    The form should look something like this
    +----------------------------------------+
    |                                        |
    |   1) _____________________________     |
    |   2) _____________________________     |
    |   .                                    |
    |   .                                    |
    |   .                                    |
    |                                        |
    |                                        |
    |                                        |
    |                                        |
    |                                        |
    |   +----+ +---------+ +--------+ +----+ |
    |   | OK | |Add Entry| | Cancel | |Next| |
    |   +----+ +---------+ +--------+ +----+ |
    +----------------------------------------+

    '''
    def __init__(self,screen,Entries,title,width=20,columns=1,back_text='Back',cancel_text='Cancel',add_entry_text='Add Entry',next_text='Next'):

        self._Buttons = snack.ButtonBar(screen, ((back_text,-1),(add_entry_text,3),(cancel_text,0),(next_text,1)))
        super(DynamicWizardEntryForm,self).__init__(Entries=Entries,screen=screen,title=title,columns=columns,width=width,Buttons=self._Buttons)

    def next(self):
        l=self.Buttons.buttonPressed(self.result)
        if l == 1 or l is None:
            return 1
        if l == 3:
            f=EntryForm(Entries=[('Add Entry','')],title='Add Entry',screen=self.screen)
            f.run()
            self.screen.popWindow()
            if f.next()==1:
                d=f.getData()['Add Entry']
                self.addEntry(label=d)
            return self
        return l

class MessageForm(BaseForm):
    '''
    This class represent a basic message box form used for messages
    '''
    def __init__(self,screen,title,msg,ok_button='OK',width=40,height=7,**kargs):
        '''
        This form will create a simple message box at the format of

        +-----------------------------+
        |                             |
        |    Message .............    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |                             |
        |          +-------+          |
        |          |  OK   |          |
        |          +-------+          |
        +-----------------------------+

        Variables:
        screen    - the screen to write to
        title     - form title
        msg          - The message to display
        ok_button - The OK button title
        width     - Text box width in columns
        height    - Text box height in lines
        scroll    - Add scrolling  1:yes 0 :no

        Addtional arguments:
        Buttons         - If the keyword Buttons is given,
        it is assumet to be a widget and added to the form insted of the Ok/Cancel Buttons
        '''
        self.TextBox=snack.Textbox(width=width,height=height,text=msg,scroll=0)
        if kargs.get('Buttons',None):
            self.Buttons=kargs['Buttons']
        else:
            self.Buttons=snack.Button(ok_button)
        super(MessageForm,self).__init__(screen,name=title,Widgets=[self.TextBox,self.Buttons])
    def next(self):
        return 1
    def setMsg(self,msg):
        '''
        Set The message
        '''
        self.TextBox.setText(msg)

class WizardMessageForm(MessageForm):
    '''
    This class represent a basic message box form used for messages.
    However it is more suitable to wizards since it contains the buttons:
    Back,Cancel,Next
    '''
    def __init__(self,screen,title,msg,width=40,height=7,**kargs):
        '''
        This form will create a simple message box at the format of

        +-----------------------------+
        |                             |
        |    Message .............    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |    .....................    |
        |                             |
        | +----+  +--------+ +----+   |
        | |Back|  | Cancel | |Next|   |
        | +----+  +--------+ +----+   |
        +-----------------------------+

        Variables:
        screen    - the screen to write to
        title     - form title
        msg       - The message to display
        ok_button - The OK button title
        width     - Text box width in columns
        height    - Text box height in lines
        scroll    - Add scrolling  1:yes 0 :no

        Addtional arguments:
        Buttons         - If the keyword Buttons is given, it is assumet to be a widget and added to the form insted of the Ok/Cancel Buttons
        '''
        if kargs.get('Buttons',None):
                self._Buttons=kargs['Buttons']
        else:
            self._Buttons=snack.ButtonBar(screen,(('Back',-1),('Cancel',0),('Next',1)))

        super(WizardMessageForm,self).__init__(screen,title,msg,scroll=scroll,height=height,width=width,Buttons=self._Buttons)

    def next(self):
        l=self._Buttons.buttonPressed(self.result)
        if not self.result or l is None:
            return 1
        return l


class YesNoForm(MessageForm):
    '''
    This will generate a message box with 2 buttons yes & no
    click on yes of pressing F12  will return 1
    click on no will return 0
    '''


    def __init__(self,screen,title,msg,height=7,width=40,scroll=0,**kargs):

                if kargs.get('Buttons',None):
                        self._Buttons=kargs['Buttons']
                else:
                        self._Buttons=snack.ButtonBar(screen,(('Yes',1),('No',0)))

                super(YesNoForm,self).__init__(screen,title,msg,scroll=scroll,height=height,width=width,Buttons=self._Buttons)

    def next(self):
            l=self._Buttons.buttonPressed(self.result)
            if not self.result or l is None:
                return 1
            return l



