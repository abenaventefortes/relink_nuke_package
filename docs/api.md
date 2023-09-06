# RelinkNukeAPI

## Overview

The  `RelinkNukeAPI`  class provides an API for managing file paths in Nuke nodes. It includes functionalities for relinking, replacing, and snapshotting node paths.

## Initialization
api = RelinkNukeAPI(new_directory, old_directory)
-  `new_directory`  - The new directory path to use for relinking. Optional.
-  `old_directory`  - The old directory path to replace. Optional.

If not provided, it will load these values from a configuration file.

## Methods

### get_all_read_nodes()

Get all read and write nodes in the Nuke script.

**Returns:** List of dicts containing node information.

### get_node_by_full_name(full_name)

Get a node by its full name.

**Parameters:** 

-  `full_name`  - The full name of the node.

**Returns:** The node object, or None if not found.

### get_new_path(node)

Get the new path for a node.

**Parameters:**

-  `node`  - The node object or a dict containing node info.

**Returns:** The new path for the node.

### find_nodes_with_paths(path_regex)

Find nodes whose paths match a regex pattern.

**Parameters:**

-  `path_regex`  - The regex pattern to match paths against.

**Returns:** List of matching node objects.

### perform_relink(old_path, new_path)

Perform the relink operation from old path to new path.

**Parameters:**

-  `old_path`  - The old path or regex pattern to match. 
-  `new_path`  - The new path to relink to.

### save_state(version, nodes)

Save the current state of the provided nodes.

**Parameters:**

-  `version`  - The version name for the state.
-  `nodes`  - List of node names to save state for.

**Returns:** True if successful.

### load_state(version)

Load a previously saved node state.

**Parameters:** 

-  `version`  - The version name of the state to load.

**Returns:** The loaded node state dict if successful.

### generate_version(type)

Generate a version identifier based on the given type.

**Parameters:**

-  `type`  - The type of version to generate (timestamp, user_input, etc) 

**Returns:** The generated version string.

### get_saved_states()

Get a list of saved states from the database.

**Returns:** A list containing the saved states.

### execute_replacement()

Execute the path replacement operation for selected nodes.

### execute_snapshot_restore() 

Restore node paths based on selected saved states.

### get_selected_snapshot_nodes()

Get nodes selected in the snapshot table. 

**Returns:** List containing node name and path.

### get_selected_states_for_restore()

Get saved states selected for restore.

**Returns:** List containing selected saved state dicts.

## Helper Methods

-  `replace_path()`  - Replace a matching path in a file path.
-  `append_replacement_path()`  - Append new directory to a file path.
-  `get_snapshot_nodes()`  - Get nodes selected in Nuke with file knobs.

## Configuration

The  `config.json`  file stores configuration settings like the  `old_directory`  and  `new_directory`  paths.

## Logging

Logging is configured to log to  `relink.log` . The  `log_message()`  method handles logging.
