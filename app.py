#!/usr/bin/python
import pymongo , math , json , bson , datetime
from gi.repository import Gtk

class app():
    
    builder = False
    mongo_conn = False
    mongo_db = False
    mongo_collection = False
    box_content = False
    window_main = False


    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui.glade")
        builder_handlers = {
            "on_window_main_delete_event": Gtk.main_quit,
            "on_button_top_connect_clicked": self.connect
        }
        self.builder.connect_signals(builder_handlers)
        self.window_main = self.o("window_main")
        self.box_content = self.o('box_content')
        
        self.windows_show_init()
        Gtk.main()


    ## Wrapper
    def o(self, obj_id):
        return self.builder.get_object(obj_id)


    def clear(self, obj):
        for o in obj.get_children():
            o.destroy()


    def status(self , msg):
        self.o('label_status').set_text(msg)


    def connect(self, obj):
        if obj.get_label() == 'Connect':
            host = self.o('entry_top_host').get_text()
            self.o('entry_top_host').set_editable(False)
            port = self.o('entry_top_port').get_text()
            self.o('entry_top_port').set_editable(False)

            obj.set_label('Connecting')
            self.status('Connecting to host ' + host + ' on port ' + port)
            
            try:
                self.mongo_conn = pymongo.Connection(host , int(port))
            except:
                self.mongo_conn = False
            
            if isinstance(self.mongo_conn , pymongo.connection.Connection):
                obj.set_label('Disconnect')
                self.status('Connected to MongoDB host successfully')
                self.windows_show_databases()
            else:
                obj.set_label('Connect')
                self.status('Error connecting to host')
                self.o('entry_top_host').set_editable(True)
                self.o('entry_top_port').set_editable(True)

        elif obj.get_label() == 'Disconnect':
            self.status('Disconnected from ' + self.mongo_conn.host)
            self.mongo_conn.disconnect()
            self.o('entry_top_host').set_editable(True)
            self.o('entry_top_port').set_editable(True)
            obj.set_label('Connect')
            self.windows_show_init()


    def windows_show_init(self):
        print 'Loading Init window'
        self.clear(self.box_content)
        self.o("window_main").show_all()
    

    def windows_show_databases(self):
        print 'Loading Databases window'
        self.clear(self.box_content)
        databases = Gtk.ListStore(str)
        for database in self.mongo_conn.database_names():
            databases.append([database])

        self.databases_view = Gtk.TreeView(databases)
        self.databases_view.append_column(Gtk.TreeViewColumn("Databases", Gtk.CellRendererText(), text=0))
        self.databases_view.get_selection().connect("changed", self.windows_show_databases_selected)
        
        self.collections_view = Gtk.TreeView(None)
        self.collections_view.append_column(Gtk.TreeViewColumn("Collections", Gtk.CellRendererText(), text=0))
        self.collections_view.append_column(Gtk.TreeViewColumn("Docs", Gtk.CellRendererText(), text=1))
        self.collections_view.get_selection().connect("changed", self.windows_show_databases_collections_selected)

        left_menu = Gtk.Box(False , 5 , orientation=Gtk.Orientation.VERTICAL)
        left_menu.pack_start(self.databases_view , True , True , 0)
        left_menu.pack_start(self.collections_view , True , True , 0)
        
        self.box_collection = Gtk.Box(False , 5 , orientation=Gtk.Orientation.VERTICAL)
        
        self.box_content.pack_start(left_menu , True , True , 0)
        self.box_content.pack_start(self.box_collection , True , True , 0)
        self.o("window_main").show_all()


    def windows_show_databases_selected(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            database = model[treeiter][0]
            print "Database selected", database
            
            collections = Gtk.ListStore(str, int)
            for collection in self.mongo_conn[database].collection_names():
                count = self.mongo_conn[database][collection].find().count()
                collections.append([collection, count])
            
            self.collections_view.set_model(collections)


    def windows_show_databases_collections_selected(self, selection):
        model, treeiter = self.databases_view.get_selection().get_selected()
        database = model[treeiter][0]

        model, treeiter = selection.get_selected()

        if treeiter != None:
            self.mongo_db = self.mongo_conn[ database ]
            collection = model[treeiter][0]
            print "Collection selected", collection
            self.mongo_collection = self.mongo_db[ collection ]
            self.windows_show_collection(collection)


    def windows_show_collection(self, collection):
        self.clear(self.box_collection)
        
        self.docs_per_page = 10
        max_pages = math.ceil( float( self.mongo_collection.find().count() ) / float( self.docs_per_page ) )
        print max_pages
        
        box_collection_menu = Gtk.Box(False , 5 , orientation=Gtk.Orientation.HORIZONTAL)
        
        box_collection_menu_button_filter = Gtk.Button('Filter')
        box_collection_menu_button_insert = Gtk.Button('Insert')
        box_collection_menu_button_update = Gtk.Button('Update')
        box_collection_menu_button_remove = Gtk.Button('Remove')
        box_collection_menu_spinbutton_page = Gtk.SpinButton()
        box_collection_menu_spinbutton_page.set_value(1)
        box_collection_menu_spinbutton_page.set_numeric(True)
        box_collection_menu_spinbutton_page.set_adjustment( Gtk.Adjustment( 1, 1, max_pages, 1, 10, 0) )
        box_collection_menu_spinbutton_page.connect('value-changed',self.populate_collection)
        
        box_collection_menu.pack_start(box_collection_menu_button_filter , False , False , 0)
        box_collection_menu.pack_start(box_collection_menu_button_insert , False , False , 0)
        box_collection_menu.pack_start(box_collection_menu_button_update , False , False , 0)
        box_collection_menu.pack_start(box_collection_menu_button_remove , False , False , 0)
        box_collection_menu.pack_start( Gtk.Label('Page:') , False , False , 0)
        box_collection_menu.pack_start(box_collection_menu_spinbutton_page , False , False , 0)

        self.box_collection.pack_start(box_collection_menu , False , False , 0)
        scroll = Gtk.ScrolledWindow()
        viewport = Gtk.Viewport()
        self.box_collection_list = Gtk.Box(False , 2 , orientation=Gtk.Orientation.VERTICAL)
        
        viewport.add( self.box_collection_list )
        scroll.add( viewport )
        self.box_collection.pack_start( scroll , True , True , 0)
        
        self.windows_show_collection
        
        self.populate_collection(False)


    def populate_collection(self,obj):
        print "Populating collection"
        self.clear(self.box_collection_list)
        if obj:
            page = obj.get_value_as_int()
        else:
            page = 1
        
        documents = self.mongo_collection.find().skip((page-1)*self.docs_per_page).limit(self.docs_per_page)
        
        for document in documents:
            expander_base = Gtk.Expander()
            if '_id' in document:
                expander_base.set_label('id: ' + str( document['_id'] ) )
            else:
                expander_base.set_label('document')
            doc = Gtk.Label()
            doc.set_line_wrap( True )
            doc.set_alignment(0, 0.5)
            doc.set_selectable(True)
            doc.set_label( self.bsondump( document ) )

            expander_base.add( doc )
            self.box_collection_list.pack_start(expander_base , False , False , 0)

        self.o("window_main").show_all()
        
    
    def bsondump(self , param , return_string = True ):
        new_json = {}
        if isinstance( param , list ):
            i = 0
            d = {}
            for p in param:
                d.setdefault( str(i) , p )
        elif isinstance( param , dict ):
            d = param
        else:
            return param

        for k,v in d.items():
            if isinstance( v , bson.objectid.ObjectId ):
                v = unicode( v )
            elif isinstance( v , datetime.datetime ):
                v = v.isoformat()
            elif isinstance( v , dict ) or isinstance( v , list ):
                v = self.bsondump( v , False )

            new_json.setdefault( k , v )
        
        if return_string:
            return json.dumps( new_json , False , True , True , True , json.JSONEncoder , 4 )
        else:
            return new_json
app()









