import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pc import PythonConsole

foo = "bar" # in global scope

def destroy_console(*args):
    Gtk.main_quit()

#ns = {'__builtins__' : __builtins__, 'foo' : foo}

ns = globals()
console = PythonConsole(namespace = ns, 
                        destroy_cb = destroy_console)
console.set_size_request(600, 400)
console.eval("print('The var foo should be accessible here!')", False)
window = Gtk.Window()
window.set_title('Interactive Python Console')
window.add(console)
window.connect('destroy', destroy_console)
window.show_all()
Gtk.main()
