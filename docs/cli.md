# Relink Nuke CLI

This command line interface allows relinking node file paths in Nuke scripts.

## Usage
relink_nuke [OPTIONS] <nuke_file>
**Arguments:**

-  `nuke_file`  - Path to the Nuke .nk file to process.

**Options:**

-  `-o, --old-path <path>`  - The old path to replace.
-  `-n, --new-path <path>`  - The new path to replace to. 
-  `--save-state <name>`  - Save current state with given name.
-  `--load-state <name>`  - Load a previously saved state.
-  `--list-states`  - List saved states.
-  `--version-type <type>`  - Version type (timestamp, user_input, auto_increment)

**Example:**

Relink nodes from  `/old/path`  to  `/new/path`  in  `script.nk` :
relink_nuke.py -o /old/path -n /new/path script.nk
## Commands

**--save-state**

Save the current state of selected nodes in the Nuke script.
--save-state v1
This will save the state and label it "v1".

**--load-state** 

Load a previously saved node state.
--load-state v1
**--list-states**

Print out a list of saved states along with their save dates.

**--version-type**

Specify the type of version identifier to use when saving states.

-  `timestamp`  - Unique timestamp string 
-  `user_input`  - Prompt user for custom name
-  `auto_increment`  - Auto increment integer

## Configuration

The  `config.json`  file stores the  `old_path`  and  `new_path`  configuration.

## Logging

The script logs to  `relink.log` .
