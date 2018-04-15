#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License version 2, as published
#   by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranties of
#   MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program.  If not, see <http://www.gnu.org/licenses/>.
#   
#   This file incorporates code from Catfish 1.4.4:
#   Copyright (C) 2007-2012 Christian Dywan <christian@twotoasts.de>
#   Copyright (C) 2012-2018 Sean Davis <smd.seandavis@gmail.com>
#   
#   The rest is:
#   Copyright (C) 2018 Sven Arvidsson <sa@whiz.se>

from gi.repository import GObject
from gi.repository import Peas
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Liferea

def find_by_name(self, name):
    """
    Finds a self by name. Searches recursively for a GtkSelf with
    matching name or buildable ID. (Both listed as "name" in GTK
    Inspector).

    Returns a GtkWidget or False if none exists with name.

    Uses get_children, and if applicable, get_submenu for GtkMenuItem
    which for some reason doesn't list these in get_children. Do other
    GTK widgets have the same pecularity?
    """

    # FIXME: Should probably return None

    all_children = []
    #byshell = shell.lookup(name)
    get_children = getattr(self, "get_children", None)
    get_submenu = getattr(self, "get_submenu", None)

    # if byshell:
    #     return byshell
    if self.get_name() == name:
        return self
    if Gtk.Buildable.get_name(self) == name:
        return self
    if get_children:
        for c in self.get_children():
            all_children.append(c)
    if get_submenu:
        submenu = self.get_submenu()
        if submenu is not None:
        # Self supports get_submenu, but has None set
            for s in self.get_submenu():
                all_children.append(s)
    
    if len(all_children) > 0:
        for child in all_children:
            childwidget = child.find_by_name(name)
            if childwidget:
                return childwidget
    else:
        return False

def find_by_type(self, wantedtype):
    """
    Returns the first child of type from widget. Returns None if none
    found.
    """
    widgettype = self.class_path()[1].split('.')[-1]
    # FIXME Is there a better way to get a human readable string for the
    # type?
    if widgettype == wantedtype:
        return self
    if getattr(self, "get_children", None):
    # FIXME: We should check for get_submenu etc too...
        for child in self.get_children():
            childmatch = child.find_by_type(wantedtype)
            if childmatch:
                return childmatch
    else:
        return None

# Monkey business!
Gtk.Widget.find_by_name = find_by_name
Gtk.Widget.find_by_type = find_by_type

class FloatingStatusBarPlugin(GObject.Object, Liferea.ShellActivatable):
    """ Replace the static statusbar with a floating one """
    __gtype_name__ = 'FloatingStatusBarPlugin'

    object = GObject.property(type=GObject.Object)
    shell = GObject.property(type=Liferea.Shell)

    def __init__(self):
        self.window = None
        self.oldtitle = None
        self.timeout = None
        self.oldstatuslabel = None
        self.unread_label = None
        self.statusbar = None
        self.unread_cb = None
        self.oldstatus_cb = None
        self.overlay = None

    def update_statusbar(self, label, gparam):
        """Update the floating statusbar with status from the old"""
        status = label.get_label()
        if status is not "":
            if self.timeout:
                GLib.source_remove(self.timeout)
            self.statusbar_label.set_label(status)
            self.statusbar.show()
            self.timeout = GLib.timeout_add_seconds(2, self.idle_hide, None)

    def idle_hide(self, widget):
        """Hide after a period of time"""
        self.statusbar.hide()
        return True

    def update_title(self, label, gparam):
        """Update title with new and unread"""
        unread = label.get_label()
        if unread is not "":
            self.window.set_title(unread + " — " + self.oldtitle)

    def on_floating_bar_enter_notify(self, statusbar, gparam):
        """Hide from the mouse cursor"""
        statusbar.hide()

    def on_floating_bar_draw(self, widget, cairo_t):
        """Draw the floating statusbar"""
        context = widget.get_style_context()

        context.save()
        context.set_state(widget.get_state_flags())

        Gtk.render_background(context, cairo_t, 0, 0,
                              widget.get_allocated_width(),
                              widget.get_allocated_height())

        Gtk.render_frame(context, cairo_t, 0, 0,
                         widget.get_allocated_width(),
                         widget.get_allocated_height())

        context.restore()
        return False

    def do_activate(self):
        """Activate plugin"""
        self.window = self.shell.get_window()
        self.oldtitle = self.window.get_title()

        leftpane = self.shell.lookup("leftpane")
        parent = leftpane.get_parent()
        self.overlay = Gtk.Overlay()
        leftpane.reparent(self.overlay) # FIXME: reparent is apparently deprecated
        parent.add(self.overlay)
        self.overlay.show()

        # The floating statusbar widget is stolen from Catfish 1.4.4:
        # Create the overlay statusbar
        self.statusbar = Gtk.EventBox()
        self.statusbar.get_style_context().add_class("background")
        self.statusbar.get_style_context().add_class("floating-bar")
        self.statusbar.connect("draw", self.on_floating_bar_draw)
        self.statusbar.connect("enter-notify-event",
                               self.on_floating_bar_enter_notify)
        self.statusbar.set_halign(Gtk.Align.START)
        self.statusbar.set_valign(Gtk.Align.END)

        # Put the statusbar in the overlay
        self.overlay.add_overlay(self.statusbar)

        # Pack the label
        self.statusbar_label = Gtk.Label()
        self.statusbar_label.show()

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        box.pack_start(self.statusbar_label, False, False, 0)
        box.set_margin_left(6)
        box.set_margin_top(3)
        box.set_margin_right(6)
        box.set_margin_bottom(3)
        box.show()

        self.statusbar.add(box)
        # START or END for right and left adjustment
        self.statusbar.set_halign(Gtk.Align.END) 
        # .... stolen code ends here :)

        # Hide the old statusbar
        self.oldstatusbar = self.shell.lookup("statusbar")
        self.oldstatusbar.hide()

        # Use the old labels with the new floating statusbar
        self.oldstatuslabel = self.oldstatusbar.find_by_name("label")
        self.oldstatus_cb = self.oldstatuslabel.connect("notify::label",
                                                        self.update_statusbar)

        # The unread/new items is in the first GtkLabel in the first
        # GtkEventBox in oldstatusbar
        self.unread_label = self.oldstatusbar.find_by_type("GtkEventBox").find_by_type("GtkLabel")
        self.unread_cb = self.unread_label.connect("notify::label",
                                                   self.update_title)
        # Update the title on plugin activation, don't wait for event
        self.update_title(self.unread_label, None)

    def do_deactivate(self):
        """Deactivate plugin"""
        # Bring children back to birth parents!
        vbox1 = self.shell.lookup("vbox1")
        leftpane = self.shell.lookup("leftpane")
        self.overlay.remove(leftpane)
        vbox1.remove(self.overlay)
        vbox1.attach(leftpane, 0, 0, 1, 1)

        # Cleanup
        self.window.set_title(self.oldtitle)
        self.oldstatusbar.show()
        if self.timeout:
            GLib.source_remove(self.timeout)
        self.oldstatuslabel.disconnect(self.oldstatus_cb)
        self.oldstatuslabel = None
        self.unread_label.disconnect(self.unread_cb)
        self.unread_label = None
        # FIXME: self.statusbar.disconnect(....
        self.statusbar = None
