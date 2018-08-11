# TODO
# Make sure accelerator Ctrl+H isn't alredy used
# Hide wideViewItems (a GtkViewPort)
# Also hide feedlist?
# Toggle button in toolbar?
# Have keynav, n/p working with headlines closed?

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Liferea

def remove_menuitem(action, menus, level=0):
    """
    Given an action name such as app.function, remove it from a Gio.Menu
    """
    for i in range(menus.get_n_items()):
        link = menus.iterate_item_links(i)
        if link.next():
            remove_menuitem(action, link.get_value(), level+1)
        else:
            attr = menus.iterate_item_attributes(i)
            while attr.next():
                if str(attr.get_name()) == "action":
                    value = str(attr.get_value()).strip("'")
                    if value == action:
                        menus.remove(i)


class HideHeadlinesPlugin(GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'HideHeadlinesPlugin'

    object = GObject.property(type=GObject.Object)
    shell = GObject.property(type=Liferea.Shell)

    def _toggle_hide(self, action, value):
        action.set_state(value)
        self._normalviewitems.props.visible = not self._normalviewitems.props.visible

    def __init__(self):
        self._normalviewitems = None
        self._viewmenu = None
        self._app = None

    def do_activate(self):
        win = self.shell.get_window()
        self._normalviewitems = self.shell.get_property("builder").get_object("normalViewItems")

        action = Gio.SimpleAction.new_stateful("HideHeadlines", None, GLib.Variant.new_boolean(False))
        action.connect("change-state", self._toggle_hide)

        self._app = win.get_application()
        self._app.add_action(action)
        self._app.set_accels_for_action("app.HideHeadlines", ["<Control>H"])

        self._viewmenu  = self.shell.get_property("builder").get_object("view_menu")
        self._viewmenu.append("Hide Headline View", "app.HideHeadlines")

    def do_deactivate(self):
        self._normalviewitems.show()
        self._app.remove_action('HideHeadlines')
        remove_menuitem("app.HideHeadlines", self._viewmenu)
