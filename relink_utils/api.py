"""
api.py

This module provides an API for managing file paths in Nuke nodes.
It includes functionalities for relinking, replacing, and snapshotting node paths.
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import List, Dict
from .database import RelinkDatabase
import nuke

# Configure logging
package_location = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(package_location, "relink.log")
logging.basicConfig(filename=log_file_path, level=logging.INFO)


def log_message(message: str):
    """Log a message to the configured log file.

    Args:
        message (str): The message to log.
    """
    logging.info(message)


class RelinkNukeAPI:
    """A class to manage file paths in Nuke nodes.

    Attributes:
        config (dict): Configuration settings.
        database (RelinkDatabase): Database for storing state.
        config_file (str): Path to the configuration file.
        old_directory (str): Old directory path.
        new_directory (str): New directory path.
    """

    def __init__(self, new_directory: str = None, old_directory: str = None):
        """Initialize the RelinkNukeAPI class.

        Args:
            new_directory (str, optional): The new directory path. Defaults to None.
            old_directory (str, optional): The old directory path. Defaults to None.
        """
        self.config = {}
        self.database = RelinkDatabase()
        self.config_file = "config.json"
        self.load_config()
        self.old_directory = self.config.get('old_directory', old_directory)
        self.new_directory = self.config.get('new_directory', new_directory)

    @staticmethod
    def get_all_read_nodes() -> List[Dict]:
        """Get all read and write nodes in the Nuke script.

        Returns:
            List[Dict]: A list of dictionaries containing node information.
        """
        read_nodes = []
        for node in nuke.allNodes(recurseGroups=True):
            if node.Class() in ['Read', 'Write'] and 'file' in node.knobs() and node['file'].value():
                read_nodes.append({
                    'node': node,
                    'full_name': node.fullName(),
                    'old_path': node['file'].value(),
                    'name': node.name(),
                    'path': node['file'].value()
                })
        return read_nodes

    @staticmethod
    def get_node_by_full_name(full_name):
        """Get a node by its full name.

        Args:
            full_name (str): The full name of the node.

        Returns:
            nuke.Node: The node object, or None if not found.
        """
        for node in nuke.allNodes(recurseGroups=True):
            if node.fullName() == full_name:
                return node
        return None

    def get_new_path(self, node):
        """Get the new path for a node.

        Args:
            node (nuke.Node or dict): The node object or a dictionary containing node information.

        Returns:
            str: The new path for the node.
        """
        if isinstance(node, dict):
            return node.get('new_path', '')
        else:
            old_path = node['old_path']
            return self.append_replacement_path(old_path)

    @staticmethod
    def find_nodes_with_paths(old_path_regex):
        """Find nodes whose paths match a given regular expression.

        Args:
            old_path_regex (str): The regular expression to match.

        Returns:
            List[nuke.Node]: A list of matching node objects.
        """
        matching_nodes = []
        for node in nuke.allNodes(recurseGroups=True):
            if node.knob('file'):
                file_path = node['file'].value()
                if re.search(old_path_regex, file_path):
                    matching_nodes.append(node)
        return matching_nodes

    def perform_relink(self, old_path_regex, new_path):
        """Perform the relink operation.

        Args:
            old_path_regex (str): The old path or a regular expression to match the old path.
            new_path (str): The new path to set.

        Returns:
            None
        """
        try:
            # Find nodes with paths that match the old path regex
            matching_nodes = self.find_nodes_with_paths(old_path_regex)
            if not matching_nodes:
                log_message("No nodes with matching paths found.")
                return

            # Perform the relink operation
            for node in matching_nodes:
                old_path = node['file'].value()
                if old_path:
                    new_path_for_node = old_path.replace(self.old_directory, self.new_directory)
                    node['file'].setValue(new_path_for_node)

            log_message(f"Successfully relinked {len(matching_nodes)} nodes.")

            # Log the relink operation and update the config
            self.database.log_relink_operation(old_path_regex, new_path)
            self.update_config(old_path_regex, new_path)

        except Exception as e:
            log_message(f"Relink failed: {e}")

    def update_config(self, old_path, new_path):
        """Update the configuration settings.

        Args:
            old_path (str): The old path.
            new_path (str): The new path.

        Returns:
            None
        """
        self.config[old_path] = new_path
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f)
        except Exception as e:
            log_message(f"Failed to save config: {e}")

    def load_config(self):
        """Load the configuration settings from the config file.

        Returns:
            None
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
                    if 'old_directory' not in self.config or 'new_directory' not in self.config:
                        log_message("Warning: Incomplete config.")
            else:
                self.config = {'old_directory': None, 'new_directory': None}
                log_message("Config file does not exist. Using defaults.")
        except json.JSONDecodeError:
            log_message("Failed to load config: Invalid JSON format")
        except Exception as e:
            log_message(f"Failed to load config: {e}")

    def update_node_path(self, node_full_name, new_path):
        """Update the file path of a node identified by its full name.

          Args:
              node_full_name (str): The full name of the node.
              new_path (str): The new file path to set for the node.

          Returns:
              None
        """
        node = self.get_node_by_full_name(node_full_name)
        if node:
            node['file'].setValue(new_path)

    def update_node_path_partial(self, node_name, matching_path, replacement_path):
        """Partially update the file path of a node identified by its name.

        Args:
            node_name (str): The name of the node.
            matching_path (str): The substring in the current path to match.
            replacement_path (str): The substring to replace the matching_path with.

        Returns:
            None
        """
        node = self.get_node_by_name(node_name)
        if node:
            current_path = node['file'].value()
            if matching_path in current_path:
                new_path = current_path.replace(matching_path, replacement_path)
                node['file'].setValue(new_path)

    def manipulate_path_based_on_regex(self, node_name, regex_pattern, replacement_string):
        """Manipulate the file path of a node based on a regular expression.

           Args:
               node_name (str): The name of the node.
               regex_pattern (str): The regular expression pattern to match in the original path.
               replacement_string (str): The string to replace the matched pattern with.

           Returns:
               str or None: The new path if successful, None otherwise.
        """
        original_path = self.get_node_path(node_name)
        if not original_path:
            return None

        try:
            new_path = re.sub(regex_pattern, replacement_string, original_path)
        except re.error as e:
            return f"Invalid regex pattern: {e}"

        return new_path

    def get_node_path(self, node_name):
        """Get the file path of a node identified by its name.

            Args:
                node_name (str): The name of the node.

            Returns:
                str or None: The file path if the node exists, None otherwise.
        """
        node = self.get_node_by_name(node_name)
        if node:
            return node['file'].value()
        return None

    @staticmethod
    def get_node_by_name(node_name):
        """Retrieve a node in the Nuke script by its name.

            Args:
                node_name (str): The name of the node to retrieve.

            Returns:
                nuke.Node or None: The node object if found, None otherwise.
        """
        for node in nuke.allNodes():
            if node['name'].value() == node_name:
                return node
        return None

    def save_state(self, version, selected_nodes):
        """Save the current state of selected nodes.

            Args:
                version (str): The version identifier for the saved state.
                selected_nodes (list): List of node names to save.

            Returns:
                bool: True if the state was successfully saved, False otherwise.
        """
        state = {}
        for node_name in selected_nodes:
            node = self.get_node_by_name(node_name)
            if node:
                file_path = node['file'].value()
                state[node_name] = file_path

        success = self.database.save_state(version, state)
        return success  # Return the success status

    def load_state(self, version):
        """Load a previously saved state.

            Args:
                version (str): The version identifier for the state to load.

            Returns:
                dict or None: The restored state if successful, None otherwise.
        """
        state = self.database.load_state(version)
        if state is None:
            print(f"No state found for version {version}")
            return None  # Indicate failure

        try:
            for node_name, path in state.items():
                node = self.get_node_by_name(node_name)
                if node and node.knob('file'):
                    node['file'].setValue(path)
                else:
                    print(f"Node {node_name} not found, skipping")
            return state  # Return the restored state
        except Exception as e:
            print(f"Error restoring state: {e}")
            return None  # Indicate failure

    def generate_version(self, version_type):
        """Generate a version identifier based on a given type.

            Args:
                version_type (str): The type of version identifier to generate ("timestamp", "user_input", "auto_increment").

            Returns:
                str: The generated version identifier.
        """
        if version_type == "timestamp":
            return datetime.now().strftime("%Y%m%d%H%M%S")
        elif version_type == "user_input":
            return input("Enter a version name: ")
        elif version_type == "auto_increment":
            last_version = self.database.get_last_version()  # Assuming you have a method to get the last version
            return str(int(last_version) + 1)
        else:
            return "default_version"

    def get_saved_states_with_dates(self) -> List[Dict[str, str]]:
        """Generate a version identifier based on a given type.

            Args:
                version_type (str): The type of version identifier to generate
                                  ("timestamp", "user_input", "auto_increment").

            Returns:
                str: The generated version identifier.
        """
        return self.database.get_saved_states_with_dates()

    def execute_replacement(self):
        """Execute the path replacement operation for selected nodes."""
        selected_nodes = self.get_selected_nodes_for_snapshot()
        if not selected_nodes:
            log_message("No nodes selected for replacement.")
            return

        for node_info in selected_nodes:
            node = node_info['node']
            new_path = self.get_new_path(node)
            if not new_path:
                log_message(f"No new path generated for node {node.name()}. Skipping.")
                continue

            if not os.path.exists(os.path.dirname(new_path)):
                log_message(f"New path {new_path} is invalid or doesn't exist. Skipping.")
                continue

            node['file'].setValue(new_path)
            log_message(f"Path for node {node.name()} successfully replaced.")

    def execute_snapshot_path_restoring(self):
        """Restore the paths of nodes based on selected saved states."""
        selected_states = self.get_selected_states_for_restoring()

        if not selected_states:
            log_message("No states selected for restoring.")
            return

        for state in selected_states:
            version = state['version']

            if not self.database.state_exists(version):  # Assuming you have a method to check if a state exists
                log_message(f"State {version} doesn't exist anymore. Skipping.")
                continue

            self.load_state(version)
            log_message(f"Successfully restored state {version}.")

    def get_selected_snapshot_nodes(self):
        """Get a list of nodes that are selected in the snapshot table.

            Returns:
                List[Dict]: A list of dictionaries containing node names and their old paths.
        """
        selected_nodes = []
        for row in range(self.snapshot_table.rowCount()):
            if self.snapshot_table.item(row, 1).checkState() == Qt.Checked:  # Check if the checkbox is checked
                node_name = self.snapshot_table.item(row, 0).text()  # Get the node name from the first column
                current_path = self.snapshot_table.item(row, 2).text()  # Get the current path from the third column
                selected_nodes.append({'node': node_name, 'old_path': current_path})
        return selected_nodes

    def get_selected_states_for_restoring(self) -> List[Dict[str, str]]:
        """Get a list of saved states that are selected for restoring.

            Returns:
                List[Dict[str, str]]: A list of dictionaries containing selected saved states.
        """
        # Assuming saved states have a 'selected' attribute or similar to determine if they're selected
        all_states = self.get_saved_states_with_dates()
        return [state for state in all_states if state['selected']]

    @staticmethod
    def replace_path(original_path, match_path, replace_path):
        """Replace a matching path in the original path with a new path.

            Args:
                original_path (str): The original file path.
                match_path (str): The path to match in the original path.
                replace_path (str): The path to replace the match_path with.

            Returns:
                str: The new path.
        """
        if original_path.startswith(match_path):
            # Remove the matching part from the original path
            relative_path = os.path.relpath(original_path, match_path)
            # Join it with the new root directory
            new_path = os.path.join(replace_path, relative_path)
            return new_path
        return original_path  # Return the original path if no match is found

    def append_replacement_path(self, old_path: str) -> str:
        """Append the new directory to the old path, replacing the old directory if present.

            Args:
                old_path (str): The old file path.

            Returns:
                str: The new file path.
        """
        if self.old_directory and self.new_directory:
            return old_path.replace(self.old_directory, self.new_directory)
        elif not self.old_directory and self.new_directory:
            return os.path.join(self.new_directory, old_path)
        elif self.old_directory and not self.new_directory:
            log_message("New directory is not set. Cannot perform append_replacement_path.")
            return old_path  # or you may raise an Exception or return None, based on your application needs
        else:
            log_message("Both old_directory and new_directory are not set. Cannot perform append_replacement_path.")
            return old_path  # or you may raise an Exception or return None, based on your application needs

    @staticmethod
    def get_snapshot_nodes() -> List[Dict]:
        """Get a list of nodes that are selected and have a file knob.

            Returns:
                List[Dict]: A list of dictionaries containing node information.
        """
        snapshot_nodes = []
        for node in nuke.allNodes(recurseGroups=True):
            if node.knob('selected') and node.knob('file'):
                snapshot_nodes.append({
                    'node': node,  # Return the node object itself
                    'name': node.name(),
                    'path': node['file'].value()
                })
        return snapshot_nodes
