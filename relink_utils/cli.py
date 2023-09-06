"""
Script to relink nodes in Nuke.

This script provides functionality to relink nodes in a Nuke script
by replacing file paths. It can also save and load node states.

Typical usage example:
  relink_nuke --old-path /old/path --new-path /new/path nuke_script.nk
"""

# Import argparse module for parsing command line arguments
import argparse

# Import nuke module to interact with Nuke
import nuke

# Import RelinkNukeAPI class from relink_utils package
from relink_utils.api import RelinkNukeAPI


def print_states(api):
    """Prints saved states with dates.

  Args:
    api (RelinkNukeAPI): The API instance.

  """

    # Get saved states from API
    states_with_dates = api.get_saved_states_with_dates()

    # Print header
    print("Saved states with dates:")

    # Loop through states and print
    for state in states_with_dates:
        print(f"Version: {state['version']}, Date: {state['date']}")


def save_state(api, state):
    """Saves the current node state.

  Args:
    api (RelinkNukeAPI): The API instance.
    state (str): The state name to save as.

  """

    # Get selected nodes from API
    selected_nodes = [node['name'] for node in api.get_snapshot_nodes()]

    # Call API method to save state
    api.save_state(state, selected_nodes)


def load_state(api, state):
    """Loads a saved node state.

  Args:
    api (RelinkNukeAPI): The API instance.
    state (str): The state name to load.

  """

    # Call API method to load state
    api.load_state(state)


def perform_relink(api, old_path, new_path):
    """Performs relink from old path to new path.

  Args:
    api (RelinkNukeAPI): The API instance.
    old_path (str): The old path to replace.
    new_path (str): The new path to replace to.

  """

    # Call API method to perform relink
    api.perform_relink(old_path, new_path)


def main():
    """Main function."""

    # Create argument parser
    parser = argparse.ArgumentParser(description="Relink nodes in Nuke.")

    # Add arguments
    parser.add_argument("nuke_file_path", type=str, help="Path to the Nuke file.")
    parser.add_argument("--old-path", type=str, help="Old path. Example: '/old/path/'")
    parser.add_argument("--new-path", type=str, help="New path. Example: '/new/path/'")
    parser.add_argument("--save-state", type=str, help="Save the current state.")
    parser.add_argument("--load-state", type=str, help="Load a saved state.")
    parser.add_argument("--list-states-with-dates", action="store_true", help="List all saved states with dates.")
    parser.add_argument("--version-type", type=str, choices=["timestamp", "user_input", "auto_increment"],
                        help="Type of versioning to use.")

    # Parse arguments
    args = parser.parse_args()

    # Create API instance
    api = RelinkNukeAPI()

    # Open Nuke script
    nuke.scriptOpen(args.nuke_file_path)

    # Define actions
    actions = {
        'list_states_with_dates': lambda: print_states(api),
        'save_state': lambda: save_state(api, args.save_state),
        'load_state': lambda: load_state(api, args.load_state),
        'old_path': lambda: perform_relink(api, args.old_path, args.new_path)
    }

    # Execute actions based on provided arguments
    for action, function in actions.items():
        if getattr(args, action):
            function()
            break
    else:
        print("Invalid or insufficient arguments provided. Use --help for usage information.")


# Check if running as standalone script
if __name__ == "__main__":
    main()
