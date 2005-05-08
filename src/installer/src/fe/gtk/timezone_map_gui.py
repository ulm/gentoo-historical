# timezone_map_gui.py: gui timezone map widget.
#
# Copyright 2001 - 2005 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#Originally written by Matt Wilson <msw@redhat.com>
#Additions by:
#Brent Fox <bfox@redhat.com>
#Nils Philippsen <nphilipp@redhat.com>

import gobject
import pango
import gtk
try:
    import gnomecanvas
except ImportError:
    import gnome.canvas as gnomecanvas
import string
import re
import math
import zonetab

##
## I18N
## 
#from rhpl.translate import _, N_
#import rhpl.translate as translate
#translate.textdomain ("system-config-date")

class Enum:
    def __init__(self, *args):
        i = 0
        for arg in args:
            self.__dict__[arg] = i
            i += 1

class TimezoneMap(gtk.VBox):
    #force order of destruction for a few items.
    def __del__(self):
        del self.arrow
        del self.markers
        del self.current

    def __init__(self, zonetab, default="America/New_York",
                 map='./map480.png'):
        gtk.VBox.__init__(self, False, 5)

        # set up class member objects
        self.zonetab = zonetab
        self.markers = {}
        self.highlightedEntry = None

        # set up the map canvas
        self.canvas = gnomecanvas.Canvas()
        root = self.canvas.root()
        pixbuf = gtk.gdk.pixbuf_new_from_file(map)
        self.mapWidth = pixbuf.get_width()
        self.mapHeight = pixbuf.get_height()
        root.add(gnomecanvas.CanvasPixbuf, x=0, y=0, pixbuf=pixbuf)
        x1, y1, x2, y2 = root.get_bounds()
        self.canvas.set_scroll_region(x1, y1, x2, y2)
        self.canvas.set_size_request(int(x2), int(y2))
        self.pack_start(self.canvas, False, False)

        self.current = root.add(gnomecanvas.CanvasText, text='x',
                                fill_color='red', anchor=gtk.ANCHOR_CENTER,
                                weight=pango.WEIGHT_BOLD)
        
        root.connect("event", self.mapEvent)
        self.canvas.connect("event", self.canvasEvent)

        self.arrow = root.add(gnomecanvas.CanvasLine,
                              fill_color='limegreen',
                              width_pixels=2,
                              first_arrowhead=False,
                              last_arrowhead=True,
                              arrow_shape_a=4.0,
                              arrow_shape_b=8.0,
                              arrow_shape_c=4.0,
                              points=(0.0, 0.0, 0.0, 0.0))
        self.arrow.hide()

        # set up status bar
        self.status = gtk.Statusbar()
        self.status.set_has_resize_grip(False)
        self.statusContext = self.status.get_context_id("")
        self.pack_start(self.status, False, False)

        self.columns = Enum("TZ", "COMMENTS", "ENTRY")
        
        # set up list of timezones
        self.listStore = gtk.ListStore(gobject.TYPE_STRING,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_PYOBJECT)

        self.currentEntry = None
        self.fallbackEntry = None
        
        for entry in zonetab.getEntries():
            iter = self.listStore.append()
            self.listStore.set_value(iter, self.columns.TZ, entry.tz)
            if entry.comments:
                self.listStore.set_value(iter, self.columns.COMMENTS,
                                         entry.comments)
            else:
                self.listStore.set_value(iter, self.columns.COMMENTS, "")
            self.listStore.set_value(iter, self.columns.ENTRY, entry)
            
            x, y = self.map2canvas(entry.lat, entry.long)
            marker = root.add(gnomecanvas.CanvasText, x=x, y=y,
                              text=u'\u00B7', fill_color='yellow',
                              anchor=gtk.ANCHOR_CENTER,
                              weight=pango.WEIGHT_BOLD)
            self.markers[entry.tz] = marker
            if entry.tz == default:
                self.currentEntry = entry

            if entry.tz == "America/New_York":
                #In case the /etc/sysconfig/clock is messed up, use New York as default
                self.fallbackEntry = entry

        self.listStore.set_sort_column_id(self.columns.TZ, gtk.SORT_ASCENDING)

        self.listView = gtk.TreeView(self.listStore)
        selection = self.listView.get_selection()
        selection.connect("changed", self.selectionChanged)
        self.listView.set_property("headers-visible", False)
        col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=0)
        self.listView.append_column(col)
        col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.listView.append_column(col)

        sw = gtk.ScrolledWindow ()
        sw.add(self.listView)
        sw.set_shadow_type(gtk.SHADOW_IN)
        self.pack_start(sw, True, True)

        self.setCurrent(self.currentEntry)

    def getCurrent(self):
        return self.currentEntry

    def selectionChanged(self, selection, *args):
        (model, iter) = selection.get_selected()
        if iter is None:
            return
        entry = self.listStore.get_value(iter, self.columns.ENTRY)
        self.setCurrent(entry, skipList=1)

    def mapEvent(self, widget, event=None):
        if event.type == gtk.gdk.MOTION_NOTIFY:
            x1, y1 = self.canvas.root().w2i(event.x, event.y)
            lat, long = self.canvas2map(x1, y1)
            last = self.highlightedEntry
            self.highlightedEntry = self.zonetab.findNearest(lat, long)
            if last != self.highlightedEntry:
                self.status.pop(self.statusContext)
                status = self.highlightedEntry.tz
                if self.highlightedEntry.comments:
                    status = "%s - %s" % (status,
                                          self.highlightedEntry.comments)
                self.status.push(self.statusContext, status)

            x2, y2 = self.map2canvas(self.highlightedEntry.lat,
                                       self.highlightedEntry.long)
            self.arrow.set(points=(x1, y1, x2, y2))
            self.arrow.show()
        elif event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 1:
                self.setCurrent(self.highlightedEntry)
                
    def setCurrent(self, entry, skipList=0):
        if not entry:
            # If the value in /etc/sysconfig/clock is invalid, default to New York
            self.currentEntry = self.fallbackEntry
        else:
            self.currentEntry = entry

        self.markers[self.currentEntry.tz].show()
        self.markers[self.currentEntry.tz].hide()
        x, y = self.map2canvas(self.currentEntry.lat, self.currentEntry.long)
        self.current.set(x=x, y=y)

        if skipList:
            return

        iter = self.listStore.get_iter_first()
        while iter:
            if self.listStore.get_value(iter, self.columns.ENTRY) == self.currentEntry:
                selection = self.listView.get_selection()
                selection.unselect_all()
                selection.select_iter(iter)
                path = self.listStore.get_path(iter)
                col = self.listView.get_column(0)
                self.listView.set_cursor(path, col, False)
                self.listView.scroll_to_cell(path, col, True, 0.5, 0.5)
                break
            iter = self.listStore.iter_next(iter)
        
    def canvasEvent(self, widget, event=None):
        if event.type == gtk.gdk.LEAVE_NOTIFY:
            self.arrow.hide()
        
    def map2canvas(self, lat, long):
        x2 = self.mapWidth
        y2 = self.mapHeight
        x = x2 / 2.0 + (x2 / 2.0) * long / 180.0
        y = y2 / 2.0 - (y2 / 2.0) * lat / 90.0
        return (x, y)

    def canvas2map(self, x, y):
        x2 = self.mapWidth
        y2 = self.mapHeight
        long = (x - x2 / 2.0) / (x2 / 2.0) * 180.0
        lat = (y2 / 2.0 - y) / (y2 / 2.0) * 90.0
        return (lat, long)

if __name__ == "__main__":
    zonetab = zonetab.ZoneTab()
    win = gtk.Window()
    if gtk.__dict__.has_key ("main_quit"):
        win.connect('destroy', gtk.main_quit)
    else:
        win.connect('destroy', gtk.mainquit)
    map = TimezoneMap(zonetab)
    vbox = gtk.VBox()
    vbox.pack_start(map)
    button = gtk.Button("Quit")
    if gtk.__dict__.has_key ("main_quit"):
        button.connect("pressed", gtk.main_quit)
    else:
        button.connect("pressed", gtk.mainquit)
    vbox.pack_start(button, False, False)
    win.add(vbox)
    win.show_all()
    if gtk.__dict__.has_key ("main"):
        gtk.main ()
    else:
        gtk.mainloop()
    
