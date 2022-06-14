from importlib import import_module

package = 'pyrpg.core.scripts.new'
module = 'show_dlg_window.py'

ref = import_module('pyrpg.core.scripts.new.show_dlg_window')

print(f'Ref: {ref}')