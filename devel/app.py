#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# @file app.py
# @brief All code for Mongui App
#
import wx , pymongo , time , datetime , bson , json , math
import wx.lib.scrolledpanel as wxScrolledPanel
from bson import json_util

##
# @brief Handles the MongoDB Connection
#
class mongodb_handler():
    ##
    # @brief Constructor - creates the 'db'
    #
    def __init__(self):
        self.db = False

    ##
    # @brief Destructor - calls Disconnect
    #
    def __del__(self):
        self.Disconnect()


    ##
    # @brief Connects to Mongo using 'host' and 'port' params
    #
    def Connect(self, host, port):
        try:
            self.db = pymongo.Connection(host , int(port))
        except:
            return False
        else:
            return self.CheckConnection()

    ##
    # @brief Disconnects from Mongo host
    #
    def Disconnect(self):
        if self.CheckConnection():
            self.db.disconnect()
            self.db = False

    ##
    # @brief Check if the connection is alive
    # @TODO fortify the check (maybe a simple query?)
    #
    def CheckConnection(self):
        if isinstance(self.db , pymongo.connection.Connection):
            return True
        else:
            return False

    
    ##
    # @brief Returns all databases names from host
    #
    def GetDatabases(self):
        if self.CheckConnection():
            return self.db.database_names()


    ##
    # @brief Returns all collections names from database in param
    #
    def GetCollections(self, database):
        if self.CheckConnection():
            return self.db[database].collection_names()
    
    
    ##
    # @brief Returns documents from database and collection params
    # @details May receive the following kwargs:
    # - find = Dict for querying the collection
    # - fields = Dict containing the fields that will return
    # - page = Int for skipping documents (starts with ZERO)
    # - limit = Int for maximum documents returned
    #
    def GetDocuments(self, database, collection, **kwargs):
        page = kwargs.get('page', 0)
        limit = kwargs.get('limit', 10)
        if page < 0:
            page = 0
        
        query = self.db[database][collection].find(kwargs.get('find', {}), fields=kwargs.get('fields', None)).skip(page * limit).limit(limit)
        
        return query
    
    
    ##
    # @brief Returns the count of documents from database and collection params
    # @details May receive the following kwargs:
    # - query = Dict for querying the collection
    #
    def CountDocuments(self, database, collection, **kwargs):
        return self.db[database][collection].find(kwargs.get('find', {}), fields=kwargs.get('fields', None)).count()

    
    ##
    # @brief Dumps the BSON in String
    #    
    def bsondump(self , param , return_string=True):
        return json.dumps(param , default=json_util.default , sort_keys=True, indent=4)

    ##
    # @brief Loads the BSON string
    #
    def bsonload(self, string):
        try:
            ret = json.loads(string.strip() , object_hook=json_util.object_hook)
        except:
            return False
        else:
            return ret

##
# @brief The first panel
#
class MainPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizerAndFit(self.sizer_main)

##
# @brief The app frame
#
class MainFrame(wx.Frame):
    ##
    # @brief Constructor - Creates the menu and the main panel
    #
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        # Build the menu bar
        MenuBar = wx.MenuBar()

        FileMenu = wx.Menu()
        ShowMenu = wx.Menu()
        
        self.menuitem_newtab = FileMenu.Append(wx.ID_ANY, text="&New Tab\tCtrl+T")
        self.menuitem_newtab.Enable(False)
        self.Bind(wx.EVT_MENU, self.OnNewTab, self.menuitem_newtab)
        
        self.menuitem_closetab = FileMenu.Append(wx.ID_ANY, text="&Close Tab\tCtrl+W")
        self.menuitem_closetab.Enable(False)
        self.Bind(wx.EVT_MENU, self.OnCloseTab, self.menuitem_closetab)
        
        FileMenu.AppendSeparator()


        self.menuitem_connect = FileMenu.Append(wx.ID_ANY, text="C&onnect...\tCtrl+Shift+C")
        self.Bind(wx.EVT_MENU, self.OnConnect, self.menuitem_connect)
        
        self.menuitem_disconnect = FileMenu.Append(wx.ID_ANY, text="&Disconnect")
        self.menuitem_disconnect.Enable(False)
        self.Bind(wx.EVT_MENU, self.OnDisconnect, self.menuitem_disconnect)
        
        FileMenu.AppendSeparator()

        menuitem_about = FileMenu.Append(wx.ID_ABOUT, text="&About")
        self.Bind(wx.EVT_MENU, self.OnAbout, menuitem_about)

        menuitem_quit = FileMenu.Append(wx.ID_EXIT, text="&Quit\tCtrl+Q")
        self.Bind(wx.EVT_MENU, self.OnQuit, menuitem_quit)


        self.menuitem_showleftpanel = ShowMenu.Append(wx.ID_ANY, text="Show &Left Panel" , kind=wx.ITEM_CHECK)
        ShowMenu.Check(self.menuitem_showleftpanel.GetId(), True)
        self.Bind(wx.EVT_MENU, self.OnShowLeftPanel, self.menuitem_showleftpanel)



        MenuBar.Append(FileMenu, "&File")
        #@TODO Fix the show/hide left panel
        #MenuBar.Append(ShowMenu, "&Show")
        self.SetMenuBar(MenuBar)

        self.Panel = MainPanel(self)
        
        #@TODO Fix the show/hide left panel
        self.sizer_leftmenu = wx.BoxSizer(wx.VERTICAL)
        
        
        
        self.tabs = wx.Notebook(self.Panel, wx.ID_ANY, style=wx.NB_TOP)
        
        self.Panel.sizer_main.Add(self.sizer_leftmenu , 0)
        self.Panel.sizer_main.Add(self.tabs , 1 , wx.EXPAND)
        
        #self.Fit()

    ##
    # @brief Closes the app
    #
    def OnQuit(self, event=None):
        self.Close()
    
    ##
    # @brief About dialog
    #
    def OnAbout(self, event=None):
        description = """MongoDB Gui"""
        licence = ""

        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon('img/mongui-logo.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Mong.ui')
        info.SetVersion('0.1a')
        info.SetDescription(description)
        #info.SetCopyright('')
        info.SetWebSite('https://github.com/viniabreulima/mongodb-gui')
        info.SetLicence(licence)
        info.AddDeveloper('Vinicius Lima (eu@viniciuslima.com)')
        #info.AddDocWriter('Vinicius Lima')
        info.AddArtist('Alexandre Sakai')
        #info.AddTranslator('')

        wx.AboutBox(info)


    ##
    # @brief Menu Connect... - Opens the Connect Dialog
    #
    def OnConnect(self, event=None):
        # First parameter is the 'parent'
        connect = ConnectDialog(self)
        connect.ShowModal()
        connect.Destroy()
        if not self.connect_window_cancelled:
            if db.CheckConnection():
                self.menuitem_disconnect.Enable(True)
                self.NewTab('clear')
            else:
                self.menuitem_disconnect.Enable(False)

    ##
    # @brief Menu Disconnect - Disconnects from MongoDB
    #
    def OnDisconnect(self, event=None):
        db.Disconnect()
        self.CloseTab('all')
        self.menuitem_newtab.Enable(False)
        if db.CheckConnection():
            self.menuitem_disconnect.Enable(True)
        else:
            self.menuitem_disconnect.Enable(False)

    ##
    # @brief Show/hide the left panel
    # @TODO Isn't working!!
    #
    def OnShowLeftPanel(self, event=None):
        if self.menuitem_showleftpanel.IsChecked():
            print 'hide'
        else:
            print 'show'

    ##
    # @brief Menu New tab - Creates a new tab
    #
    def OnNewTab(self, event=None):
        self.NewTab('last')

    ##
    # @brief Menu Close Tab - Closes the current tab
    #
    def OnCloseTab(self, event=None):
        self.CloseTab('current')

    ##
    # @brief Creates a new tab, according to the params
    #
    def NewTab(self, param):
        if param == 'clear':
            self.CloseTab('all')

        self.tabs.AddPage(ContentTab(self.tabs) , 'New Tab')
        
        self.menuitem_newtab.Enable(True)
        if self.tabs.GetPageCount() > 1:
            self.menuitem_closetab.Enable(True)
        
        self.Layout()

    ##
    # @brief Closes the tab, according to the params
    #
    def CloseTab(self, param):
        if param == 'all':
            self.tabs.DeleteAllPages()
        
        elif param == 'current':
            self.tabs.DeletePage(self.tabs.GetSelection())

        self.menuitem_closetab.Enable(self.tabs.GetPageCount() > 1)



##
# @brief The Connect dialog
#
class ConnectDialog(wx.Dialog):
    
    ##
    # @brief Constructor
    #
    def __init__(self, *args, **kw):
        super(ConnectDialog, self).__init__(*args, **kw)
        
        self.Parent.connect_window_cancelled = True
        
        self.SetTitle("Connect")

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        flexgrid_inputs = wx.FlexGridSizer(3, 2, 10, 10)
        flexgrid_inputs.SetFlexibleDirection = wx.HORIZONTAL
        
        label_host = wx.StaticText(self, label="Host: ")
        label_port = wx.StaticText(self, label="Port: ")
        
        self.input_host = wx.TextCtrl(self, size=(150, -1), value='localhost' , style=wx.TE_PROCESS_ENTER)
        self.input_host.Bind(wx.EVT_TEXT_ENTER , self.OnConnect)
        self.input_port = wx.TextCtrl(self, size=(150, -1) , style=wx.TE_PROCESS_ENTER)
        self.input_port.Bind(wx.EVT_TEXT_ENTER , self.OnConnect)
        self.button_connect = wx.Button(self, label='Connect')
        self.button_connect.Bind(wx.EVT_BUTTON , self.OnConnect)
        
        flexgrid_inputs.AddMany([
              (label_host)
            , (self.input_host , 0 , wx.EXPAND)
            , (label_port)
            , (self.input_port , 0 , wx.EXPAND)
            , (wx.StaticText(self))
            , (self.button_connect)
        ])
        
        sizer_main.Add(flexgrid_inputs, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        self.SetSizer(sizer_main)

        self.SetAutoLayout(1)
        sizer_main.Fit(self)
        self.Show()
        
        self.input_host.SetFocus()

    ##
    # @brief Event handler for connect button
    #
    def OnConnect(self, event=None):
        host = self.input_host.GetValue()
        port = 27017
        if self.input_port.GetValue() != '':
            port = self.input_port.GetValue()
        if db.Connect(host , port):
            self.Parent.connect_window_cancelled = False
            self.Destroy()
        else:
            wx.MessageBox('Error connecting to host', 'Error', wx.OK | wx.ICON_ERROR)


##
# @brief The content tab
#
class ContentTab(wx.Panel):
    ##
    # @brief Constructor
    #
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.manager = ContentManager(self)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Building Top Menu
        sizer_topmenu = wx.BoxSizer(wx.HORIZONTAL)
        self.combobox_database = wx.ComboBox(self , wx.ID_ANY , style=wx.CB_READONLY)
        self.combobox_database.Bind(wx.EVT_COMBOBOX , self.OnSelectDatabase)    
        self.combobox_collection = wx.ComboBox(self , wx.ID_ANY , style=wx.CB_READONLY)
        self.combobox_collection.Bind(wx.EVT_COMBOBOX , self.OnSelectCollection)
        
        self.togglebutton_querypanel = wx.ToggleButton(self , wx.ID_ANY , label="Query Panel")
        self.togglebutton_querypanel.Bind(wx.EVT_TOGGLEBUTTON , self.OnToggleQueryPanel)
        self.spinctrl_page = wx.SpinCtrl(self, wx.ID_ANY , value='')
        self.spinctrl_page.Bind(wx.EVT_SPINCTRL , self.OnChangePage)
        self.label_pages = wx.StaticText(self , wx.ID_ANY , label='')

        sizer_topmenu.AddMany([
              (wx.StaticText(self, wx.ID_ANY , label="Database: ") , 0 , wx.EXPAND)
            , (self.combobox_database , 0 , wx.EXPAND)
            , (wx.StaticText(self, wx.ID_ANY , label="Collection: ") , 0, wx.EXPAND)
            , (self.combobox_collection , 0 , wx.EXPAND)
        ])
        sizer_topmenu.AddSpacer(10)
        sizer_topmenu.Add(self.togglebutton_querypanel , 0)
        sizer_topmenu.AddSpacer(10)
        sizer_topmenu.AddMany([
              (wx.StaticText(self, wx.ID_ANY , label="Page: ") , 0, wx.EXPAND)
            , (self.spinctrl_page , 0 , wx.EXPAND)
            , (self.label_pages , 0 , wx.EXPAND)
        ])
        
        self.sizer.Add(sizer_topmenu , 0 , wx.EXPAND)
        
        # Building Splitter
        self.splitter = wx.SplitterWindow(self, style=wx.SP_3D)

        # Building Query Panel
        self.panel_query = QueryPanel(self.splitter, self.manager)

        # Building Content Panel
        self.scrollpanel_content = wxScrolledPanel.ScrolledPanel(self.splitter)
        self.flexsizer_content = wx.FlexGridSizer(50, 1, 2, 2)
        self.flexsizer_content.SetFlexibleDirection(wx.VERTICAL)

        self.scrollpanel_content.SetSizer(self.flexsizer_content)
        #self.scrollpanel_content.SetAutoLayout(1)

        # Joining all together
        self.splitter.Initialize(self.scrollpanel_content)
        self.splitter.Bind(wx.EVT_SPLITTER_DCLICK , self.OnSplitterSashDclick)
        self.sizer.Add(self.splitter , 1 , wx.EXPAND)
        
        self.PopulateWithDatabases(self.combobox_database)
        self.SetSizerAndFit(self.sizer)

        self.Refresh()

        self.combobox_database.SetFocus()


    ##
    # @brief Double Click Sash Splitter - Prevents the remove 
    #
    def OnSplitterSashDclick(self, event=None):
        event.Veto()

    ##
    # @brief Combobox Databases change - Lists the collections in Combobox Collections 
    #
    def OnSelectDatabase(self, event=None):
        self.Parent.SetPageText(self.Parent.GetSelection()  , 'New Tab')
        self.flexsizer_content.Clear(True)
        self.manager.enable_buttons = False
        self.PopulateWithCollections(self.combobox_collection , event.GetString())
        self.Refresh()
        self.combobox_collection.SetFocus()

    ##
    # @brief Combobox Collections change - Shows the documents and set the tab name
    #
    def OnSelectCollection(self, event=None):
        self.Parent.SetPageText(self.Parent.GetSelection()  , self.combobox_collection.GetValue())
        self.manager.ShowDocuments()
        self.spinctrl_page.SetFocus()

    ##
    # @brief Spin Control Page change - Shows the documents for the new page
    #
    def OnChangePage(self, event=None):
        self.manager.ShowDocuments()

    ##
    # @brief Populates the obj with databases names from active connection
    #
    def PopulateWithDatabases(self, obj):
        obj.SetValue('')
        obj.Clear()
        for database in sorted( db.GetDatabases() ):
            obj.Append(database)


    ##
    # @brief Populates the obj with collection names from the database param
    #
    def PopulateWithCollections(self, obj, database):
        obj.SetValue('')
        obj.Clear()
        for collection in sorted( db.GetCollections(database) ):
            obj.Append(collection)


    ##
    # @brief Toggle Button Query Panel Click - Show/hide the query panel
    #
    def OnToggleQueryPanel(self, event=None):
        if self.togglebutton_querypanel.GetValue():
            # Shows Panel
            self.splitter.SplitVertically(self.panel_query, self.scrollpanel_content)
        else:
            # Hides Panel
            self.splitter.Unsplit(toRemove=self.panel_query)

        self.Refresh(buttons=False)
    ##
    # @brief Recalculate the layout
    #
    def Refresh(self, **kwargs):
        self.panel_query.Layout()
        self.scrollpanel_content.Layout()
        self.scrollpanel_content.SetupScrolling(scrollToTop=False)
        self.splitter.Layout()
        if kwargs.get('buttons', True):
            self.RefreshButtons()
    
    ##
    # @brief Recalculate the control buttons
    #
    def RefreshButtons(self):
        if self.manager.enable_buttons:
            self.togglebutton_querypanel.Enable(True)
            self.spinctrl_page.Enable(True)
            max_pages = int(math.ceil(float(self.manager.CountDocuments()) / float(self.manager.LIMITPERPAGE)))
            self.spinctrl_page.SetRange(1 , max_pages)
            self.label_pages.SetLabel('of ' + str(max_pages) + ' pages')
        else:
            self.togglebutton_querypanel.Enable(False)
            self.togglebutton_querypanel.SetValue(False)
            self.spinctrl_page.Enable(False)
            self.spinctrl_page.SetValue(1)
            self.label_pages.SetLabel('')

##
# @brief Manages the content in ScrolledPanel in ContentTab
#
class ContentManager():
    
    # @brief Sets the limit of documents per page
    LIMITPERPAGE = 25

    ##
    # @brief Constructor
    #
    def __init__(self, tab):
        self.enable_buttons = False
        self.tab = tab
        self.query_object_find = {}
        self.query_object_fields = None

    ##
    # @brief Returns the documents total number from active tab
    #
    def CountDocuments(self):
        database = self.tab.combobox_database.GetValue()
        collection = self.tab.combobox_collection.GetValue()
        return db.CountDocuments(database , collection , find=self.query_object_find , fields=self.query_object_fields)

    ##
    # @brief Renders the documents for the active tab
    # @TODO Make the document more 'interactive'
    #
    def ShowDocuments(self):
        database = self.tab.combobox_database.GetValue()
        collection = self.tab.combobox_collection.GetValue()

        self.tab.flexsizer_content.Clear(True)
        for document in db.GetDocuments(database , collection , find=self.query_object_find , fields=self.query_object_fields , page=self.tab.spinctrl_page.GetValue() - 1 , limit=self.LIMITPERPAGE):
            self.enable_buttons = True
            self.tab.flexsizer_content.Add(DocumentRenderer(parent=self.tab.scrollpanel_content, document=document, onclick=self.OnDocumentClick))
        
        self.tab.Refresh()

    ##
    # @brief Document clicked - Refreshs the layout to accept the new document size
    #
    def OnDocumentClick(self):
        self.tab.Refresh(buttons=False)

    
    ##
    # @brief 
    #
    def SetQueryObject(self, **kwargs):
        if isinstance(kwargs.get('find', {}) , dict):
            self.query_object_find = kwargs.get('find', {})
        else:
            self.query_object_find = {}
            
        if isinstance(kwargs.get('fields', None) , dict):
            if kwargs.get('fields', None) == {}:
                self.query_object_fields = None
            else:
                self.query_object_fields = kwargs.get('fields', None)
        else:
            self.query_object_fields = None
        
        if kwargs.get('reset_page', True):
            self.tab.spinctrl_page.SetValue(1)
            
##
# @brief Stores the document data, widgets and events
#
class DocumentRenderer(wx.BoxSizer):
    ##
    # @brief Constructor
    #
    def __init__(self, **kwargs):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        self.document = kwargs.get('document')
        self.parent = kwargs.get('parent')
        self.onclick = kwargs.get('onclick')

        document_text = db.bsondump(self.document)
        
        if '_id' in self.document:
            collapsible_label = '_id: ' + str(self.document['_id'])
        else:
            collapsible_label = 'document without id'

        collapsible = wx.CollapsiblePane(self.parent , wx.ID_ANY , label=collapsible_label)
        collapsible.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED , self.OnDocumentClick)
        
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Monospace')
        
        #self.content = wx.TextCtrl(collapsible.GetPane() , wx.ID_ANY , value=document_text , style=wx.TE_READONLY | wx.TE_MULTILINE )
        self.content = wx.StaticText(collapsible.GetPane() , wx.ID_ANY , label=document_text)
        self.content.SetFont(font)

        

        self.Add(collapsible , 1 , wx.GROW)
        


    ##
    # @brief Collapsible Pane Document clicked - Executes the onclick param from parent
    #
    def OnDocumentClick(self, event=None):
        #print self.content.GetBestSize()
        #self.content.SetBestFittingSize()
        self.onclick()


##
# @brief The Query Panel for querying the collection
#
class QueryPanel(wx.Panel):
    ##
    # @brief Constructor
    #
    def __init__(self, parent, manager):
        wx.Panel.__init__(self, parent)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.parent = parent
        self.manager = manager
        
        self.sizer_leftmenu = wx.BoxSizer(wx.VERTICAL)
        self.togglebuttons_tabs = [
              wx.ToggleButton(self , wx.ID_ANY , label='Find' , name='find')
            , wx.ToggleButton(self , wx.ID_ANY , label='Update', name='update')
            , wx.ToggleButton(self , wx.ID_ANY , label='Remove', name='remove')
            , wx.ToggleButton(self , wx.ID_ANY , label='Aggregate', name='aggregate')
        ]
        for b in self.togglebuttons_tabs:
            self.sizer_leftmenu.Add(b , 0 , wx.EXPAND)
            b.Bind(wx.EVT_TOGGLEBUTTON , self.OnChangeTab)
        
        self.sizer_leftmenu.AddSpacer(10)
        
        self.button_execute = wx.Button(self , wx.ID_ANY , label='Execute')
        self.button_execute.Bind(wx.EVT_BUTTON , self.OnExecute)

        self.sizer_leftmenu.Add(self.button_execute , 0 , wx.EXPAND)
        
        self.sizer.Add(self.sizer_leftmenu , 0 , wx.EXPAND)
        
        self.sizer_content = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer.Add(self.sizer_content , 1 , wx.EXPAND)

        self.togglebuttons_tabs[0].SetValue(True)
        self.ChangeTab(self.togglebuttons_tabs[0].GetName())

        self.SetSizerAndFit(self.sizer)

    ##
    # @brief Tabs Toggle Button Click - calls ChangeTab 
    #    
    def OnChangeTab(self, event=None):
        if event.EventObject.GetValue():
            for b in self.togglebuttons_tabs:
                b.SetValue(False)
        event.EventObject.SetValue(True)
        self.ChangeTab(event.EventObject.GetName())
    
    ##
    # @brief Changes the content from sizer_content
    #
    def ChangeTab(self, tab):
        self.sizer_content.Clear(True)
        if tab == 'find':
            self.execute_param = 'find'
            font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Monospace')
            self.input_find = wx.TextCtrl(self , wx.ID_ANY , style=wx.TE_PROCESS_TAB | wx.TE_MULTILINE)
            self.input_find.SetFont(font)
            self.sizer_content.Add(wx.StaticText(self , wx.ID_ANY , label='Find Object') , 0 , wx.EXPAND)
            self.sizer_content.Add(self.input_find , 1 , wx.EXPAND)
            
            self.input_fields = wx.TextCtrl(self , wx.ID_ANY , style=wx.TE_PROCESS_TAB | wx.TE_MULTILINE)
            self.input_fields.SetFont(font)
            self.sizer_content.Add(wx.StaticText(self , wx.ID_ANY , label='Fields Object') , 0 , wx.EXPAND)
            self.sizer_content.Add(self.input_fields , 1 , wx.EXPAND)
            
            self.input_find.SetFocus()
        elif tab == 'update':
            pass
        elif tab == 'remove':
            pass
        elif tab == 'aggregate':
            pass

        self.sizer_content.Layout()
    ##
    # @brief Execute Button Click - executes the query
    # @todo Improve json parser to accept datetime, objectid, etc
    #    
    def OnExecute(self, event=None):
        if self.execute_param == 'find':
            find_value = self.input_find.GetValue().strip()
            if find_value == '':
                find_obj = {}
            else:
                find_obj = db.bsonload(find_value)

            fields_value = self.input_fields.GetValue().strip()
            if fields_value == '':
                fields_obj = {}
            else:
                fields_obj = db.bsonload(fields_value)


            if find_obj != False and fields_obj != False:
                self.manager.SetQueryObject(find=find_obj, fields=fields_obj)
                self.manager.ShowDocuments()
            else:
                wx.MessageBox('Invalid JSON object', 'Error', wx.OK | wx.ICON_ERROR)

        else:
            print event


###################################################################################################

if __name__ == '__main__':
    db = mongodb_handler()
    app = wx.App()
    frame = MainFrame(None, title="Mongui - MongoDB Gui", size=(900, 500))
    frame.SetIcon(wx.Icon('img/mongui-icon.ico', wx.BITMAP_TYPE_ICO , 16 , 16))
    frame.Show()
    app.MainLoop()


