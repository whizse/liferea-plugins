# FIXME
# find_by_name needs work

# TODO
# Make sure accelerator Ctrl+H isn't alredy used
# Hide wideViewItems (a GtkViewPort)
# Also hide feedlist?
# Toggle button in toolbar?

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Liferea
from gi.repository import Gdk

def find_by_name(widget, name):
    get_children = getattr(widget, "get_children", None)
    if widget.get_name() == name:
        return widget
    elif get_children is not None:
        children = widget.get_children()
        if len(children) > 0:
            # widget has children
            for child in children:
                childwidget = find_by_name(child, name)
                if childwidget:
                    return childwidget
        else:
            return False
    else:
        return False


class MassOpenPlugin (GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'HideHeadlinesPlugin'

    object = GObject.property(type=GObject.Object)
    shell = GObject.property(type=Liferea.Shell)

    def _toggle_hide(self, *args):
        self._normalviewitems.props.visible = not self._normalviewitems.props.visible
        return False

    def __init__(self):
        self._hide_menuitem = None
        self._hide_menuitem_cb = None
        
        self._window = None
        self._viewmenu = None
        self._normalviewitems = None

    def do_activate(self):
        self._window = self.shell.get_window()
        self._normalviewitems = self.shell.lookup("normalViewItems")
        self._viewmenu = find_by_name(self._window, "ViewMenu")
        
        self._hide_menuitem = Gtk.CheckMenuItem(label="Hide Headline View")
        self._hide_menuitem_cb = self._hide_menuitem.connect("activate",
                                                             self._toggle_hide)

        accel = Gtk.AccelGroup()
        self._window.add_accel_group(accel)

        self._hide_menuitem.add_accelerator("activate", accel, Gdk.KEY_h,
                                            Gdk.ModifierType.CONTROL_MASK,
                                            Gtk.AccelFlags.VISIBLE)
        self._viewmenu.get_submenu().append(self._hide_menuitem)
        self._hide_menuitem.show()

    def do_deactivate(self):
        self._normalviewitems.show()
        self._hide_menuitem.disconnect(self._hide_menuitem_cb)
        self._viewmenu.get_submenu().remove(self._hide_menuitem)
