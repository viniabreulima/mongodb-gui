#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# @file app.py
# @brief All code for Mongui App
#
import wx , pymongo , time , datetime , bson , json , math
import  wx.lib.scrolledpanel as wxScrolledPanel

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
        print "Disconnecting"
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
    # - query = Dict for querying the collection
    # - fields = Dict containing the fields that will return
    # - page = Int for skipping documents (starts with ZERO)
    # - limit = Int for maximum documents returned
    #
    def GetDocuments(self, database, collection, **kwargs):
        query_object = kwargs.get('query', {})
        fields_object = kwargs.get('fields', None)
        
        page = kwargs.get('page', 0)
        limit = kwargs.get('limit', 10)
        
        query = self.db[database][collection].find(query_object, fields=fields_object).skip(page * limit).limit(limit)
        
        return query
    
    
    ##
    # @brief Returns the count of documents from database and collection params
    # @details May receive the following kwargs:
    # - query = Dict for querying the collection
    #
    def CountDocuments(self, database, collection, **kwargs):
        query_object = kwargs.get('query', {})
        return self.db[database][collection].find(query_object).count()

    
    ##
    # @brief Dumps the BSON in String
    #    
    def bsondump(self , param , return_string=True):
        new_json = {}
        if isinstance(param , list):
            i = 0
            d = {}
            for p in param:
                d.setdefault(str(i) , p)
        elif isinstance(param , dict):
            d = param
        else:
            return param

        for k, v in d.items():
            if isinstance(v , bson.objectid.ObjectId):
                v = unicode(v)
            elif isinstance(v , datetime.datetime):
                v = v.isoformat()
            elif isinstance(v , dict) or isinstance(v , list):
                v = self.bsondump(v , False)

            new_json.setdefault(k , v)
        
        if return_string:
            return json.dumps(new_json , False , True , True , True , json.JSONEncoder , 4)
        else:
            return new_json
        
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


        self.menuitem_connect = FileMenu.Append(wx.ID_ANY, text="C&onnect...\tCtrl+C")
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
        licence = """The licence"""

        info = wx.AboutDialogInfo()

        #info.SetIcon(wx.Icon('path.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Mongui')
        info.SetVersion('0.1a')
        info.SetDescription(description)
        #info.SetCopyright('')
        info.SetWebSite('https://github.com/viniabreulima/mongodb-gui')
        info.SetLicence(licence)
        info.AddDeveloper('Vinicius Lima')
        #info.AddDocWriter('Vinicius Lima')
        #info.AddArtist('')
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
            print 'New connection'
            if db.CheckConnection():
                self.menuitem_disconnect.Enable(True)
                self.NewTab('clear')
            else:
                self.menuitem_disconnect.Enable(False)
        else:
            print 'Connect window cancelled'
    ##
    # @brief Menu Disconnect - Disconnects from MongoDB
    #
    def OnDisconnect(self, event=None):
        db.Disconnect()
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
        print 'Close tab'
       
        if param == 'all':
            self.tabs.DeleteAllPages()
        
        elif param == 'current':
            self.tabs.DeletePage(self.tabs.GetSelection())

        self.menuitem_closetab.Enable( self.tabs.GetPageCount() > 1 )



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
        self.input_host.Bind( wx.EVT_TEXT_ENTER , self.OnConnect )
        self.input_port = wx.TextCtrl(self, size=(150, -1) , style=wx.TE_PROCESS_ENTER)
        self.input_port.Bind( wx.EVT_TEXT_ENTER , self.OnConnect )
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
            print 'Connection successful'
            self.Parent.connect_window_cancelled = False
            self.Destroy()
        else:
            wx.MessageBox('Error connecting to host', 'Error', wx.OK | wx.ICON_ERROR)
            print 'Error connecting'


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
        
        sizer_topmenu = wx.BoxSizer(wx.HORIZONTAL)
        self.combobox_database = wx.ComboBox(self , wx.ID_ANY , style=wx.CB_READONLY)
        self.combobox_database.Bind(wx.EVT_COMBOBOX , self.OnSelectDatabase)    
        self.combobox_collection = wx.ComboBox(self , wx.ID_ANY , style=wx.CB_READONLY)
        self.combobox_collection.Bind(wx.EVT_COMBOBOX , self.OnSelectCollection)
        
        self.togglebutton_querypanel = wx.ToggleButton(self , wx.ID_ANY , label="Query Panel")
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
        
        self.scrollpanel_content = wxScrolledPanel.ScrolledPanel(self)
        self.flexsizer_content = wx.FlexGridSizer(50, 1, 2, 2)
        self.flexsizer_content.SetFlexibleDirection(wx.VERTICAL)

        self.scrollpanel_content.SetSizer(self.flexsizer_content)
        self.scrollpanel_content.SetAutoLayout(1)

        self.sizer.Add(self.scrollpanel_content , 1 , wx.EXPAND)
        
        self.PopulateWithDatabases(self.combobox_database)
        self.SetSizerAndFit(self.sizer)
        
        self.Refresh()
        
        self.combobox_database.SetFocus()

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
        for database in db.GetDatabases():
            obj.Append(database)


    ##
    # @brief Populates the obj with collection names from the database param
    #
    def PopulateWithCollections(self, obj, database):
        obj.SetValue('')
        obj.Clear()
        for collection in db.GetCollections(database):
            obj.Append(collection)


    ##
    # @brief Recalculate the layout
    #
    def Refresh(self, **kwargs):
        self.scrollpanel_content.Layout()
        self.scrollpanel_content.SetupScrolling(scrollToTop=False)
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
    LIMITPERPAGE = 10

    ##
    # @brief Constructor
    #
    def __init__(self, tab):
        self.enable_buttons = False
        self.tab = tab

    ##
    # @brief Returns the documents total number from active tab
    #
    def CountDocuments(self):
        database = self.tab.combobox_database.GetValue()
        collection = self.tab.combobox_collection.GetValue()
        return db.CountDocuments(database , collection)

    ##
    # @brief Renders the documents for the active tab
    # @TODO Make the document more 'interactive'
    #
    def ShowDocuments(self):
        database = self.tab.combobox_database.GetValue()
        collection = self.tab.combobox_collection.GetValue()

        self.tab.flexsizer_content.Clear(True)
        for document in db.GetDocuments(database , collection , page=self.tab.spinctrl_page.GetValue() - 1 , limit=self.LIMITPERPAGE):
            self.enable_buttons = True
            document_text = db.bsondump(document)
            
            if '_id' in document:
                collapsible_label = '_id: ' + str(document['_id'])
            else:
                collapsible_label = 'document without id'

            collapsible = wx.CollapsiblePane(self.tab.scrollpanel_content , wx.ID_ANY , label=collapsible_label)
            collapsible.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED , self.OnDocumentClick)
            wx.StaticText(collapsible.GetPane() , wx.ID_ANY , label=document_text)

            container = wx.BoxSizer(wx.VERTICAL)
            container.Add(collapsible , 1 , wx.GROW)
            self.tab.flexsizer_content.Add(container)
        
        self.tab.Refresh()
    
    ##
    # @brief Collapsible Pane Document clicked - Refreshs the layout to accept the new document size
    #
    def OnDocumentClick(self, event=None):
        self.tab.Refresh(buttons=False)

###################################################################################################

if __name__ == '__main__':
    db = mongodb_handler()
    app = wx.App()
    frame = MainFrame(None, title="Mongui - MongoDB Gui", size=(900, 500))
    frame.Show()
    app.MainLoop()


