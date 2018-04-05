# Simple plugin to disable Mark All As Read
#
# Copyright 2018 Sven Arvidsson <sa@whiz.se>
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

from gi.repository import GObject, Gtk
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

class MarkAllReadInactivePlugin (GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'SetMarkAllFeedsAsReadInactive'

    object = GObject.property(type=GObject.Object)
    shell = GObject.property(type=Liferea.Shell)

    def __init__(self):
        self.menuitem = None

    def do_activate(self):
        if self.menuitem is None:
            win = self.shell.get_window()
            self.menuitem = find_by_name(win, self.shell,
                                         "MarkAllFeedsAsRead")
            self.menuitem.set_sensitive(False)
            toolbarbutton = find_by_name(win, self.shell,
                                         "MarkAsReadButton")
            # Liferea toggles the sensitivity on the ToolButton on and
            # off, so we target the child Button instead

            # FIXME: This needs a function that returns the first
            # child widget of matching type
            self.markasreadbutton = toolbarbutton.get_children()[0]
            self.markasreadbutton.set_sensitive(False)
            
    def do_deactivate(self):
        self.menuitem.set_sensitive(True)
        self.markasreadbutton.set_sensitive(True)
        
