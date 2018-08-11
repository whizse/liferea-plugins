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

class MarkAllReadInactivePlugin (GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'SetMarkAllFeedsAsReadInactive'

    object = GObject.property(type=GObject.Object)
    shell = GObject.property(type=Liferea.Shell)

    def __init__(self):
        self.action = None
        self.toolbarbutton = None
        
    def do_activate(self):
        self.app = self.shell.get_window().get_application()
        self.action = self.app.lookup_action('mark-all-feeds-read')
        self.app.remove_action('mark-all-feeds-read')

        self.toolbarbutton = self.shell.lookup("MarkAsReadButton")
        self.toolbarbutton.set_sensitive(False)

    def do_deactivate(self):
        self.app.add_action(self.action)
        self.action = None

        self.toolbarbutton.set_sensitive(True)
        self.toolbarbutton = None
