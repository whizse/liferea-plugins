#!/usr/bin/python3
#
# Liferea Dark Mode Plugin
#
# Copyright (C) 2018 Sven Arvidsson <sa@whiz,se>
#
# Based on the Inspector plugin:
#
# Copyright (C) 2015 Mozbugbox <mozbugbox@yahoo.com.au>
# Copyright (C) 2018 Lars Windolf <lars.windolf@gmx.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; see the file COPYING.LIB.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# FIXME/TODO
#
# Prefs panel to select CSS styles
# GSettings to remember last style used
# Load name of css style from comment with "Name: "
# Make CSS loading bulletproof
# - Try (os.path.abspath(os.path.dirname(__file__))
# - Try os.path.join(GLib.get_user_data_dir(), "liferea", "plugins", "dark-mode", "css", "dark_1.css")
# - Try os.path.join(GLib.get_user_data_dir(), "liferea", "plugins", "css", "dark_1.css")
# - Fallback on inline CSS.
# Throw an error on plugin loading if JS/CSS is not found and let the user sort it out before reloading plugin.
# Use JS to load CSS:
# - serve from a custom handler for css://
# - Check URI against a blacklist for sites to ignore
# - Check URI and serve site specific css.
# Button in toolbar to switch between styles?

import os, gi
gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, PeasGtk, Liferea, WebKit2, GLib

class DarkModePlugin (GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = "DarkModePlugin"

    object = GObject.property (type=GObject.Object)
    shell = GObject.property (type=Liferea.Shell)

    _shell = None
    css = ""

    def __init__(self):
        GObject.Object.__init__(self)

    @property
    def main_webkit_view(self):
        """Return the webkit webview in the item_view"""
        shell = self._shell
        item_view = shell.props.item_view
        if not item_view:
            print("Item view not found!")
            return None

        htmlv = item_view.props.html_view
        if not htmlv:
            print("HTML view not found!")
            return None

        return htmlv

    @property
    def current_webviews(self):
        """Get all the available webviews """
        views = []
        webkit_view = self.main_webkit_view
        if webkit_view is None:
            return views
        views.append(webkit_view.props.renderwidget)

        browser_tabs = self._shell.props.browser_tabs
        box_in_tabs = [x.htmlview for x in browser_tabs.props.tab_info_list]
        html_in_tabs = [x.props.renderwidget for x in box_in_tabs]
        views.extend(html_in_tabs)
        return views

    @property
    def browser_notebook(self):
        """Return the notebook of browser_tabs"""
        browser_tabs = self._shell.props.browser_tabs
        bt_notebook = browser_tabs.props.notebook
        return bt_notebook

    def do_activate (self):
        """Override Peas Plugin entry point"""
        if self._shell is None:
            DarkModePlugin._shell = self.props.shell

        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        csspath = os.path.join(GLib.get_user_data_dir(), "liferea", "plugins", "dark-mode", "css", "dark_1.css")
        with open(csspath) as fd:
            self.css = fd.read()

        current_views = self.current_webviews
        for v in current_views:
            self.hook_webkit_view(v)

        # watch new webkit view in browser_tabs
        bt_notebook = self.browser_notebook
        cid = bt_notebook.connect("page-added", self.on_tab_added)
        bt_notebook.shades_page_added_cid = cid

    def do_deactivate (self):
        """Peas Plugin exit point"""
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", False)
        
        current_views = self.current_webviews
        if current_views:
            for v in current_views:
                self.unhook_webkit_view(v)

        bt_notebook = self.browser_notebook
        bt_notebook.disconnect(bt_notebook.shades_page_added_cid)
        del bt_notebook.shades_page_added_cid

    def on_tab_added(self, noteb, child, page_num, *user_data_dummy):
        """callback for new webview tab creation"""
        self.hook_webkit_view(child.get_children()[1])

    def hook_webkit_view(self, wk_view):
        cm = wk_view.get_user_content_manager()
        # https://lazka.github.io/pgi-docs/#WebKit2-4.0/classes/UserStyleSheet.html#WebKit2.UserStyleSheet
        frames = WebKit2.UserContentInjectedFrames.TOP_FRAME
        level = WebKit2.UserStyleLevel.USER
        whitelist = None
        blacklist = None
        stylesheet = WebKit2.UserStyleSheet(self.css, frames, level,
                                            whitelist, blacklist)
        cm.add_style_sheet(stylesheet)

    def unhook_webkit_view(self, wk_view):
        cm = wk_view.get_user_content_manager()
        # Don't think we can remove single scripts/css, so this will
        # screw up other plugins running their own usercontent!
        cm.remove_all_style_sheets()
