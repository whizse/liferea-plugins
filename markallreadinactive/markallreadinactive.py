from gi.repository import GObject
from gi.repository import Liferea


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
    __gtype_name__ = 'SetMarkAllFeedsAsReadInactive'

    object = GObject.property(type=GObject.Object)
    shell = GObject.property(type=Liferea.Shell)

    def __init__(self):
        self.menuitem = None

    def do_activate(self):
        if self.menuitem is None:
            win = self.shell.get_window()
            menu = find_by_name(win, "SubscriptionsMenu")
            self.menuitem = find_by_name(menu.get_submenu(),
                                         "MarkAllFeedsAsRead")
            self.menuitem.set_sensitive(False)

    def do_deactivate(self):
        self.menuitem.set_sensitive(True)
