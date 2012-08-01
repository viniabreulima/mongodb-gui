#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# @file app.py
# @brief All code for Mongui App
#
import wx , pymongo , time , datetime , bson , json

##
# @brief Handles the MongoDB Connection
#
class mongodb_handler():
    db = False
    def __init__(self):
        pass

    def __del__(self):
        self.Disconnect()

    def Connect(self, host, port):
        try:
            self.db = pymongo.Connection(host , int(port))
        except:
            return False
        else:
            return self.CheckConnection()

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
        MenuBar.Append(ShowMenu, "&Show")
        self.SetMenuBar(MenuBar)

        self.Panel = MainPanel(self)
        
        self.sizer_leftmenu = wx.BoxSizer(wx.VERTICAL)
        self.sizer_leftmenu.Add( wx.TextCtrl(self.Panel, wx.ID_ANY) , 0 )
        
        self.tabs = wx.Notebook(self.Panel, wx.ID_ANY, style=wx.NB_TOP)
        self.Panel.sizer_main.Add( self.sizer_leftmenu , 0 )
        self.Panel.sizer_main.Add( self.tabs , 1 , wx.EXPAND )
        
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
        if db.CheckConnection():
            self.menuitem_disconnect.Enable(True)
        else:
            self.menuitem_disconnect.Enable(False)

    ##
    # @brief Show/hide the left panel
    # @TODO Isn't working!!
    #
    def OnShowLeftPanel(self,event=None):
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
    def NewTab(self,param):
        if param =='clear':
            self.CloseTab('all')
            
        print 'New tab'
        self.tabs.AddPage( ContentTab(self.tabs) , 'tab' )
        
        self.menuitem_newtab.Enable(True)
        if self.tabs.GetPageCount() > 1:
            self.menuitem_closetab.Enable(True)
        
        self.Layout()

    ##
    # @brief Closes the tab, according to the params
    #
    def CloseTab(self,param):
        print 'Close tab'

        if self.tabs.GetPageCount() <= 1:
            self.menuitem_closetab.Enable(False)
        
        if param == 'current':
            print self.tabs.GetSelection()
            self.tabs.DeletePage( self.tabs.GetPage( self.tabs.GetSelection() ) )



##
# @brief The Connect dialog
#
class ConnectDialog(wx.Dialog):
    
    ##
    # @brief Constructor
    #
    def __init__(self, *args, **kw):
        super(ConnectDialog, self).__init__(*args, **kw) 
        self.SetTitle("Connect")

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        flexgrid_inputs = wx.FlexGridSizer(3, 2, 10, 10)
        flexgrid_inputs.SetFlexibleDirection = wx.HORIZONTAL
        
        label_host = wx.StaticText(self, label="Host: ")
        label_port = wx.StaticText(self, label="Port: ")
        
        self.input_host = wx.TextCtrl(self, size=(150, -1), value='localhost')
        self.input_port = wx.TextCtrl(self, size=(150, -1))
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
            self.Destroy()
        else:
            wx.MessageBox('Error connecting to host', 'Error', wx.OK | wx.ICON_ERROR)
            print 'Error connecting'



##
# @brief The content tab
#
class ContentTab(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add( wx.Button(self,wx.ID_ANY,label='test') )
        self.sizer.Add( wx.TextCtrl(self,wx.ID_ANY) )
        self.SetSizerAndFit(self.sizer)
        

if __name__ == '__main__':
    db = mongodb_handler()
    app = wx.App()
    frame = MainFrame(None, title="Mongui - MongoDB Gui")
    frame.Show()
    app.MainLoop()


