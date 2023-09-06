# Relink Database

The relink database is a SQLite database used to store relink history and saved node states. 

## Overview

The database contains two tables:

-  `relink_history`  - Stores history of relink operations
-  `saved_states`  - Stores saved node states labeled with a version

The  `RelinkDatabase`  class provides methods to interact with this database.

## Usage
from relink_utils.database import RelinkDatabase

db = RelinkDatabase()
The database file  `relink_database.db`  will be created in the package data directory.

### Logging Relink Operations

To log a relink operation:
db.log_relink(old_path_regex, new_path)
This will add a new row to the  `relink_history`  table.

### Saving/Loading States
# Save state
success = db.save_state("v1", state_dict) 

# Load state
state = db.load_state("v1")
States are saved as JSON in the  `saved_states`  table. 

### Other Methods

-  `get_saved_states()` : Get a list of all saved versions
-  `get_last_version()` : Get the last saved version string
-  `state_exists(version)` : Check if a state exists

## Schema

**relink_history**

| Column | Type | Info |
|-|-|-|  
| id | INTEGER | Primary key |
| timestamp | TIMESTAMP | Defaults to current time |
| old_path_regex | TEXT | Old path regex pattern |
| new_path | TEXT | New path |
| use_regex | INTEGER | Whether regex was used |
| affected_nodes | INTEGER | Number of nodes affected |

**saved_states**

| Column | Type | Info |
|-|-|-|
| id | INTEGER | Primary key | 
| version | TEXT | State version (unique) |
| state | TEXT | JSON encoded state dict |
| timestamp | TIMESTAMP | Defaults to current time |
