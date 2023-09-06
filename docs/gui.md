# Relink Nuke GUI

GUI application built with PySide2 for relinking Nuke node paths.

## Overview

The GUI provides:

- A replacement tool to relink paths
- Snapshot functionality to save and restore node states
- Customizable options for relinking like regex

It uses the  `RelinkNukeAPI`  class to interface with Nuke.

## Usage

The GUI is launched as a standalone PySide2 application:
from relink_nuke_gui import RelinkNukeGUI

app = QApplication()
window = RelinkNukeGUI()
window.show()
app.exec_()
## Interface

The interface contains:

### Main Window

- Title: Relink Nuke Tool
- Reload Button: Refresh all data
- Tabs: For replacement tool and snapshot

### Replacement Tab

- Table: For selecting nodes and entering new paths
- Options: Default and regex options for matching paths
- Execute: Button to run replacement

### Snapshot Tab  

- Current Nodes: Table for selecting nodes to snapshot 
- Saved States: Table showing saved versions
- Save: Button to save snapshot of selected nodes
- Restore: Restore nodes to a previous state

## Code Overview

Key classes and methods:

-  `RelinkNukeGUI` : Main GUI window
  -  `update_tables()` : Refreshes all data
  -  `execute_replacement()` : Runs replacement on selected nodes
-  `RelinkNukeAPI` : Backend API 
  -  `replace_path()` : Relinks an individual node
  -  `save_snapshot()` : Saves node states
  -  `load_snapshot()` : Restores node states
