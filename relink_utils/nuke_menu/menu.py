import nuke
import sys

# sys path manipulation
# This line will be dynamically added by the install_menu() method on install_script.py
# sys.path.append('your_package_root_path_here')

# Declare global_panel_reference as a global variable at the top of your script
global_panel_reference = None

print(sys.path)

# Import RelinkNukeGUI
print("Before import attempt.")
try:
    from relink_utils.gui import RelinkNukeGUI

    print("Successfully imported RelinkNukeGUI.")
except ImportError as err:
    print("Failed to import RelinkNukeGUI.")
    print(err)
    import traceback

    traceback.print_exc()


def show_relink_nuke_gui():
    global global_panel_reference
    global_panel_reference = RelinkNukeGUI()
    global_panel_reference.show()


# Add menu item
nuke.menu('Nuke').addCommand('relink_plugin/Show Relink Nuke GUI', 'show_relink_nuke_gui()')
