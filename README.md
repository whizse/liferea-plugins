# Liferea plugins #
Place in ~/.local/share/liferea/plugins or what your `$XDG_DATA_DIRS`
points to.

##  Disable Mark All As Read ##
Disables the menu entry for "Subscriptions" &rarr; "Mark All As Read"
as it is a little bit too easy to hit by mistake. Also disables the
toolbar button.

It does not disable the same functionality in the context menu for
feeds and folders.

##  Hide Headline View ##
Adds a menu entry (View &rarr; Hide Headline View) and a keyboard shortcut
(Ctrl+H) to hide the headline view. 

Makes it easier (less scrolling) to read articles on small screens.

##  Python Console ##
Interactive Python Console for Liferea! Simplifies writing and
debugging plugins. 

Based on the plugin for Rhythmbox, which in turn was based on gEdit and
Epiphany. 99.9% of the work is not mine, I do take credit for the new
bugs in this version.

##  Floating statusbar ##
Regain some screen real estate by replacing the static statusbar with
a floating counterpart. Similar to the ones used in web browsers. 

Uses code gratefully borrowed from the Catfish file searching tool,
thank you guys!

This is an experimental plugin that reparents some UI elements in the
main Liferea window.

## Dark Mode ##
Enables the dark GTK theme variant with matching dark CSS
override. This plugin is heavily based on the [inspector plugin](https://github.com/lwindolf/liferea-webkit2-inspector) and the
[Firefox WebExtension Dark Mode](https://mybrowseraddon.com/dark-mode.html).

For now it uses a single theme. Plans include support for all the
variants shipped with the Firefox extension as well as site specific
styles and a blacklist for sites to exclude.

## utilities ##
Not a plugin. Small utilities I re-use for plugins.
