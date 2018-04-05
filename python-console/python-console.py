from gi.repository import GObject, Peas, Gtk
from gi.repository import Liferea

from pc import PythonConsole

class PythonConsolePlugin(GObject.Object, Liferea.ShellActivatable):
    __gtype_name__ = 'PythonConsolePlugin'

    shell = GObject.property(type=Liferea.Shell)
    
    def __init__(self):
        GObject.Object.__init__(self)
        self.console_window = None

    def do_activate(self):
        self._ui_manager = self.shell.get_property("ui-manager")

        console_action = Gtk.Action('PythonConsole', 'Python Console', 'Run the Python console', None)
        console_action.connect("activate", self.show_console, self.shell)

        self._actiongroup = Gtk.ActionGroup("PythonConsoleAction")
        self._actiongroup.add_action(console_action)

        self._ui_manager.insert_action_group(self._actiongroup)
        self._console_action_id = self._ui_manager.add_ui_from_string(
                  """<ui>
                        <menubar name='MainwindowMenubar'>
                          <menu action='ToolsMenu'>
                            <menuitem action='PythonConsole'/>
                          </menu>
                        </menubar>
                     </ui>""")

    def do_deactivate(self):
        self._ui_manager.remove_action_group(self._actiongroup)
        # Removing action group does not remove the UI elements
        self._ui_manager.remove_ui(self._console_action_id)
        if self.console_window is not None:
            self.console_window.destroy()

    def show_console(self, parameter, shell):
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
