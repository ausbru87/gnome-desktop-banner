import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from Xlib.display import Display
from Xlib import X

class Banner:

    def __init__(self, fgcolor, bgcolor, font, size, font_weight, banner_height, vertical_offset=0, message=""):
        self.banner_height = banner_height
        self.message = message
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.font = font
        self.size = size
        self.font_weight = font_weight
        self.banner_height = banner_height
        self.vertical_offset = vertical_offset

        # Create an undecorated dock
        self.window = Gtk.Window()
        self.window.set_name("bar")
        self.window.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.window.set_decorated(False)
        self.window.set_keep_above(True)  # Keep the window always on top
        self.window.stick()  # Make the window visible on all workspaces
        self.window.connect("delete-event", Gtk.main_quit)

        # Style it
        style_provider = Gtk.CssProvider()
        css_data = b"""
        #bar {
            background-color: %s;
        }
        """ % self.bgcolor.encode('utf-8')
        style_provider.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Display.get_default().get_default_screen(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Add a label to the center of the bar
        center_label = Gtk.Label()
        center_label.set_markup(
            "<span font_family='%s' font_weight='%s' foreground='%s' size='%s'>%s</span>" % (
                self.font, self.font_weight, self.fgcolor, self.size, self.message))
        center_label.set_justify(Gtk.Justification.CENTER)
        center_label.set_yalign(0.5)
        center_label.set_xalign(0.5)
        center_label.set_hexpand(True)
        center_label.set_vexpand(True)
        self.window.add(center_label)
        self.window.show_all()

        # Initialize display and monitor
        self.display = Display()
        self.topw = self.display.create_resource_object('window',
                                                        self.window.get_toplevel().get_window().get_xid())
        self.auto_resize()

    def auto_resize(self, event=None):

        monitor = Gdk.Display.get_default().get_primary_monitor()
        geometry = monitor.get_geometry()

        x = geometry.x
        y = geometry.y
        width = geometry.width
        #height = geometry.height (REMOVING TO SEE IF IT IS NEEDED)

        # Adjust y position to be below the status bar only for the primary monitor
        y += self.vertical_offset

        # Move and resize the window
        self.window.move(x, y)
        self.window.resize(width, self.banner_height)

        # Reserve space (a "strut") for the bar
        strut_top = self.banner_height + self.vertical_offset
        self.topw.change_property(self.display.intern_atom('_NET_WM_STRUT'),
                             self.display.intern_atom('CARDINAL'), 32,
                             [0, 0, strut_top, 0],
                             X.PropModeReplace)
        self.topw.change_property(self.display.intern_atom('_NET_WM_STRUT_PARTIAL'),
                             self.display.intern_atom('CARDINAL'), 32,
                             [0, 0, strut_top, 0, 0, 0, 0, 0, x, x + width - 1, 0, 0],
                             X.PropModeReplace)