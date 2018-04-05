# TODO
# Make sure accelerator Ctrl+H isn't alredy used
# Hide wideViewItems (a GtkViewPort)
# Also hide feedlist?
# Toggle button in toolbar?

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Liferea

def find_by_name(widget, shell, name):
    """
    Finds a widget by name. Searches recursively for a GtkWidget with
    matching name or buildable ID. (Both listed as "name" in GTK
    Inspector).

    Returns a GtkWidget or False if none exists with name.

    Uses get_children, and if applicable, get_submenu for GtkMenuItem
    which for some reason doesn't list these in get_children. Do other
    GTK widgets have the same pecularity?
    """

    # FIXME: Should probably return None
    # FIXME: get rid of shell.lookup?

    all_children = []
    byshell = shell.lookup(name)
    get_children = getattr(widget, "get_children", None)
    get_submenu = getattr(widget, "get_submenu", None)

    if byshell:
        return byshell
    if widget.get_name() == name:
        return widget
    if Gtk.Buildable.get_name(widget) == name:
        return widget
    if get_children:
        for c in widget.get_children():
            all_children.append(c)
    if get_submenu:
        submenu = widget.get_submenu()
        if submenu is not None:
        # Widget supports get_submenu, but has None set
            for s in widget.get_submenu():
                all_children.append(s)
    
    if len(all_children) > 0:
        for child in all_children:
            childwidget = find_by_name(child, shell, name)
            if childwidget:
                return childwidget
    else:
        return False

class HideHeadlinesPlugin(GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'HideHeadlinesPlugin'

    object = GObject.property(type=GObject.Object)
    shell = GObject.property(type=Liferea.Shell)

    def _toggle_hide(self, *args):
        self._normalviewitems.props.visible = not self._normalviewitems.props.visible

    def __init__(self):
        self._hide_menuitem = None
        self._hide_menuitem_cb = None
        
        self._viewmenu = None
        self._normalviewitems = None

    def do_activate(self):
        win = self.shell.get_window()
        self._normalviewitems = find_by_name(win, self.shell, "normalViewItems")
        self._viewmenu = find_by_name(win, self.shell, "ViewMenu")
        
        self._hide_menuitem = Gtk.CheckMenuItem(label="Hide Headline View")
        self._hide_menuitem_cb = self._hide_menuitem.connect("activate",
                                                             self._toggle_hide)

        accel = Gtk.AccelGroup()
        win.add_accel_group(accel)

        self._hide_menuitem.add_accelerator("activate", accel, Gdk.KEY_h,
                                            Gdk.ModifierType.CONTROL_MASK,
                                            Gtk.AccelFlags.VISIBLE)
        self._viewmenu.get_submenu().append(self._hide_menuitem)
        self._hide_menuitem.show()

    def do_deactivate(self):
        self._normalviewitems.show()
        self._hide_menuitem.disconnect(self._hide_menuitem_cb)
        self._viewmenu.get_submenu().remove(self._hide_menuitem)
