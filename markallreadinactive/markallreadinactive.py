# Simple plugin to disable Mark All As Read
#
# Copyright 2016 Sven Arvidsson <sa@whiz.se>
#
# This plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
