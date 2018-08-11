from gi.repository import GObject, Peas, Gtk, Gio
from gi.repository import Liferea

from pc import PythonConsole

class PythonConsolePlugin(GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'PythonConsolePlugin'

    shell = GObject.property(type=Liferea.Shell)
    
    def __init__(self):
        GObject.Object.__init__(self)
        self.console_window = None

    def do_activate(self):
        action = Gio.SimpleAction.new('PythonConsole', None)
        self.x = action.connect("activate", self.show_console, self.shell)

        self._app = self.shell.get_window().get_application ()
        self._app.add_action(action)

        self.toolsmenu = self.shell.get_property("builder").get_object("tools_menu")
        self.toolsmenu.append('Python Console', 'app.PythonConsole')

    def do_deactivate(self):
        # FIXME: removes action but not the menu entry
        # this doesn't seem possible in a Gio.Menu
        self._app.remove_action('PythonConsole')

        if self.console_window is not None:
            self.console_window.destroy()

    def show_console(self, action, variant, shell):
        if not self.console_window:
            ns = {'__builtins__' : __builtins__, 
                  'Liferea' : Liferea,
                  'shell' : shell}
            console = PythonConsole(namespace = ns, 
                                    destroy_cb = self.destroy_console)
            console.set_size_request(600, 400)
            console.eval('print("' + \
                         _("You can access the main window " \
                         "through the \'shell\' variable :") +
                         '\\n%s" % shell)', False)

            self.console_window = Gtk.Window()
            self.console_window.set_title('Lifera Python Console')
            self.console_window.add(console)
            self.console_window.connect('destroy', self.destroy_console)
            self.console_window.show_all()
        else:
            self.console_window.show_all()
        self.console_window.grab_focus()
    
    def destroy_console(self, *args):
        self.console_window.destroy()
        self.console_window = None
