# Installation

## Requirements
- Python 3.7+ 
- Nuke 11+

## Install with pip
To install the Relink Nuke plugin using pip, cd in to the directory and run:

`pip install .`

This will install the package and dependencies.


## Install Plugin Menu
The  `install_script.py`  handles installing the plugin menu in Nuke. 

It can be run in CLI mode:

`relink_nuke_plugin --menu`

Or in GUI mode without any arguments:

`relink_nuke_plugin`

The script will:

- Prompt for the menu.py path, or use the default Nuke directory
- Back up menu.py if enabled
- Copy over the new menu.py file
- Insert/replace the sys.path manipulation line

So after running the install script, you will have a new "Relink Nuke" menu in Nuke.

## Uninstalling
pip uninstall relink-nuke-plugin
And remove the menu.py modifications.

Let me know if you would like me to expand on any part of this documentation further!