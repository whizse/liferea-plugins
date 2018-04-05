from gi.repository import Gtk

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

# !!!!!!!!!!!!!!!!!!!!!!
# FIXME: This needs a function that returns the first
# child widget of matching type
#self.markasreadbutton = toolbarbutton.get_children()[0]

    
def list_names(widget, names):
    """Recursively finds the name or buildable id for a GtkWidget and all
    children and submenus. Ignores names starting with "Gtk".

    Checks for buildable id first. It will be None if not set.
    .get_name on a GtkWidget on the other hand returns the widget
    type, e.g. GtkWindow, if name is not set

    Uses get_children, and if applicable, get_submenu for GtkMenuItem
    which for some reason doesn't list these in get_children. Do other
    GTK widgets have the same pecularity?
    """

    buildid = Gtk.Buildable.get_name(widget)
    if buildid:
        names.append(buildid)
    else:
        gtkname = widget.get_name()
        if not "Gtk" in gtkname[:3]:
            names.append(gtkname)

    children = []
    if getattr(widget, "get_children", None):
        for child in widget.get_children():
            children.append(child)

    if getattr(widget, "get_submenu", None):
        # Widget has get_submenu method but returns None
        submenu = widget.get_submenu()
        if submenu is not None:
            for sub in widget.get_submenu():
                children.append(sub)

    if len(children) > 0:
        for child in children:
            list_names(child, names)
    else:
        return False

def hierarchy(widget, level=0):
    """
    Prints a hierarchy of GtkWidgets and children to stdout. Compare
    to the output of GTK Inspector.

    Uses get_children, and if applicable, get_submenu for GtkMenuItem
    which for some reason doesn't list these in get_children. Do other
    GTK widgets have the same pecularity?
    """
    
    name = Gtk.Buildable.get_name(widget)
    if not name:
        name = widget.get_name()

    space = ""
    for i in range(0, level):
        space += " "
    print(space + name + " (" + str(widget) + ")")
    
    children = []
    if getattr(widget, "get_children", None):
        for child in widget.get_children():
            children.append(child)

    if getattr(widget, "get_submenu", None):
        submenu = widget.get_submenu()
        # Widget has get_submenu method but returns None
        if submenu is not None:            
            for sub in widget.get_submenu():
                children.append(sub)

    if len(children) > 0:
        for child in children:
            hierarchy(child, level+1)
    else:
        return False

hierarchy(shell.get_window())

# x = find_by_name(shell.get_window(), shell, "MarkAllFeedsAsRead")
# print(x)
# print(x.get_name())
# print(names)

# Needs to handle internal children
# sub = find_by_name(shell.get_window(), shell, "SubscriptionsMenu")
# print(sub)
# submenu = sub.get_submenu()
# for c in submenu.get_children():
#     print(c.get_name())
# print(sub)
# print("External children: ")
# print(sub.get_children())
# sub.forall(cb, None)

# names.append("Foo") # Non-match

names = []
list_names(shell.get_window(), names)
#print(names)

for item in names:
    look = find_by_name(shell.get_window(), shell, item)
    print((item, look))
    # print()
    # if not look:
    #     print("Not found")
    #     print((item, look))
