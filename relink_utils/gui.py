"""
relink_nuke_gui.py

GUI application for relinking paths in Nuke using PySide2.
TODO: Finish refactoring this code, add docstrings/ code block comments and node color logic
"""
import re

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QHeaderView,
    QMessageBox,
    QCheckBox,
    QApplication
)

from .api import RelinkNukeAPI


class RelinkNukeGUI(QMainWindow):
    """Main GUI window for the relink tool."""

    def __init__(self):
        """Initializes the GUI by setting up the main widget and layout.

        Creates an instance of RelinkNukeAPI and initializes the tables
        and tabs. Loads initial data by calling update_tables().
        """
        super().__init__()
        self.api = RelinkNukeAPI()
        self.node_states = {}
        self.snapshot_data = []

        self.setWindowTitle("Relink Nuke Tool")
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout()
        self.main_widget.setLayout(layout)

        reload_button = QPushButton("Reload Tables")
        reload_button.clicked.connect(self.update_tables)
        layout.addWidget(reload_button)

        # Initialize tables
        self.init_tables()
        # Initialize tabs
        self.init_tabs()
        # Add Tabs to layout
        layout.addWidget(self.tabs)

        # Initialize your table here...
        self.update_tables()
        self.toggle_edit_mode(Qt.Unchecked)

    def init_tabs(self):
        """Initializes the tab widgets.

        Creates a QTabWidget and adds the replacement tools and
        snapshot tabs to it.
        """
        self.tabs = QTabWidget()
        # Initialization of the Replacement Tools Tab
        self.replacement_tools_tab = QWidget()
        self.init_replacement_tools_content()
        self.tabs.addTab(self.replacement_tools_tab, "Replacement Tools")
        # Initialization of the Snapshot Tab
        self.snapshot_tab = QWidget()
        self.init_snapshot_content()
        self.tabs.addTab(self.snapshot_tab, "Snapshot")

    def init_replacement_tools_content(self):
        """Sets up the content for the replacement tools tab.

        Adds the edit mode checkbox, node table, replacement options
        tabs, and execute button to the layout.
        """
        layout = QVBoxLayout(self.replacement_tools_tab)
        # Edit mode checkbox
        self.edit_mode_checkbox = QCheckBox("Edit Mode")
        self.edit_mode_checkbox.stateChanged.connect(self.toggle_edit_mode)
        layout.addWidget(self.edit_mode_checkbox)  # Moved here
        # Node table
        layout.addWidget(self.table)
        # Add Replacement Options Tabs (Default, Regex)
        replacement_options_tabs = QTabWidget()
        self.init_default_tab()
        self.init_regex_tab()
        replacement_options_tabs.addTab(self.default_tab, "Default")
        replacement_options_tabs.addTab(self.regex_tab, "Regex")
        layout.addWidget(replacement_options_tabs)
        # Add Execute Replacement Button
        execute_button = QPushButton("Execute Path Replacement")
        execute_button.clicked.connect(self.execute_path_replacement)
        layout.addWidget(execute_button)

    def init_snapshot_content(self):
        """Sets up the content for the snapshot tab.

        Adds the current nodes, saved states, and the save/restore
        buttons to the layout.
        """

        layout = QVBoxLayout(self.snapshot_tab)

        # Current Nodes
        layout.addWidget(QLabel("Current Nodes"))
        layout.addWidget(self.snapshot_table)
        # Saved States
        layout.addWidget(QLabel("Saved States"))
        layout.addWidget(self.saved_states_table)
        # Save and Restore buttons
        self.save_state_btn = QPushButton("Save State")
        self.save_state_btn.clicked.connect(self.create_snapshot)

        self.restore_path_state_btn = QPushButton("Restore Path State")
        self.restore_path_state_btn.clicked.connect(self.restore_path_state)

        layout.addWidget(self.save_state_btn)
        layout.addWidget(self.restore_path_state_btn)
        self.tabs.addTab(self.snapshot_tab, "Snapshot")

    def init_tables(self):
        """Initializes the data tables.

        Creates the replacement tools table, snapshot table, and
        saved states table with the required columns.
        """

        # Initialize Replacement Tools Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Node", "Select", "Current Path", "New Path"])
        self.table.itemChanged.connect(self.handle_item_changed)  # Add this line
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Initialize Snapshot Table
        self.snapshot_table = QTableWidget(0, 3)
        self.snapshot_table.setHorizontalHeaderLabels(["Node", "Select", "Current Path"])
        self.snapshot_table.itemChanged.connect(self.handle_item_changed)  # Add this line
        self.snapshot_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.snapshot_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Initialize Saved States Table
        self.saved_states_table = QTableWidget(0, 3)  # Added an extra column for 'Select'
        self.saved_states_table.setHorizontalHeaderLabels(
            ["Version Name", "Select", "Current Paths"])  # Renamed to plural and reordered
        self.saved_states_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.saved_states_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def execute_path_replacement(self):
        """Executes path replacement on selected nodes.

        Iterates through selected rows and calls api.replace_path()
        to replace the path. Shows message boxes on errors.
        """

        for row in range(self.table.rowCount()):
            if self.table.item(row, 1).checkState() == Qt.Checked:
                node_full_name = self.table.item(row, 0).text()
                node = self.api.get_node_by_full_name(node_full_name)

                if node is None:
                    QMessageBox.warning(self, "Path Replacement", f"Node {node_full_name} not found.")
                    continue  # Skip the rest of this iteration

                current_path = node['file'].value()
                new_path = self.table.item(row, 3).text()

                success = self.api.replace_path(current_path, current_path, new_path)

                if success:
                    self.node_states[node_full_name] = 'replaced'  # <-- This line updates the state
                    new_item = QTableWidgetItem(new_path)

                    if self.edit_mode_checkbox.checkState() != Qt.Checked:
                        new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)

                    self.table.setItem(row, 3, new_item)  # Update New Path here
                    # Update the actual node path in Nuke
                    self.api.update_node_path(node_full_name, new_path)
                else:
                    QMessageBox.warning(self, "Path Replacement", f"Failed to replace path for node {node_full_name}.")

                # Reset the "New Path" field for this row
                self.table.setItem(row, 3, QTableWidgetItem(""))

        # Refresh the table (optional, if needed)
        self.update_tables()

    def init_node_table(self):
        node_table_layout = QVBoxLayout()
        self.replacement_tools_tab.setLayout(node_table_layout)
        node_table_layout.addWidget(self.table)

    def init_default_tab(self):
        self.default_tab = QWidget()
        default_tab_layout = QVBoxLayout()
        self.default_tab.setLayout(default_tab_layout)
        self.matching_path_field = QLineEdit()
        self.replacement_path_field = QLineEdit()
        # Connect textChanged signals to generate_new_path slot
        self.matching_path_field.textChanged.connect(self.generate_new_path)
        self.replacement_path_field.textChanged.connect(self.generate_new_path)
        default_tab_layout.addWidget(QLabel("Matching Path:"))
        default_tab_layout.addWidget(self.matching_path_field)
        default_tab_layout.addWidget(QLabel("Replacement Path:"))
        default_tab_layout.addWidget(self.replacement_path_field)

    def init_regex_tab(self):
        self.regex_tab = QWidget()
        regex_tab_layout = QVBoxLayout()
        self.regex_tab.setLayout(regex_tab_layout)
        self.regex_pattern_field = QLineEdit()
        self.regex_new_path_field = QLineEdit()
        regex_test_button = QPushButton("Test")
        regex_test_button.clicked.connect(self.test_regex)
        regex_tab_layout.addWidget(QLabel("Regex Pattern:"))
        regex_tab_layout.addWidget(self.regex_pattern_field)
        regex_tab_layout.addWidget(QLabel("New Path:"))
        regex_tab_layout.addWidget(self.regex_new_path_field)
        regex_tab_layout.addWidget(regex_test_button)
        self.tabs.addTab(self.regex_tab, "Regex")
        self.regex_pattern_field.textChanged.connect(self.generate_new_path_with_regex)
        self.regex_new_path_field.textChanged.connect(self.generate_new_path_with_regex)

    def init_snapshot_tab(self):
        self.snapshot_tab = QWidget()
        snapshot_tab_layout = QVBoxLayout()
        self.snapshot_tab.setLayout(snapshot_tab_layout)
        # Table for Current Nodes
        snapshot_tab_layout.addWidget(QLabel("Current Nodes"))
        snapshot_tab_layout.addWidget(self.snapshot_table)
        # Table for Saved States
        snapshot_tab_layout.addWidget(QLabel("Saved States"))
        snapshot_tab_layout.addWidget(self.saved_states_table)
        # Buttons for Save State and Restore Path State
        self.save_state_btn = QPushButton("Save State")
        self.restore_path_state_btn = QPushButton("Restore Path State")
        self.save_state_btn.clicked.connect(self.create_snapshot)
        # For this button, you'd have to write a method that implements the restore functionality
        self.restore_path_state_btn.clicked.connect(self.restore_path_state)
        snapshot_tab_layout.addWidget(self.save_state_btn)
        snapshot_tab_layout.addWidget(self.restore_path_state_btn)
        self.tabs.addTab(self.snapshot_tab, "Snapshot")

    def handle_item_changed(self, item):
        table = item.tableWidget()
        node_name = table.item(item.row(), 0).text()
        if item.column() == 1:  # The checkbox column
            if item.checkState() == Qt.Checked:
                self.node_states[node_name] = 'selected'
            else:
                self.node_states[node_name] = 'unselected'

    def choose_version_to_restore(self):
        for row in range(self.saved_states_table.rowCount()):
            if self.saved_states_table.item(row, 1).checkState() == Qt.Checked:  # Check the 'Select' column
                selected_version = self.saved_states_table.item(row, 0).text()
                return selected_version
        QMessageBox.warning(self, "Snapshot", "No saved states selected.")
        return None

    def restore_path_state(self):
        selected_version = self.choose_version_to_restore()
        if selected_version is not None:
            restored_state = self.api.load_state(
                selected_version)  # This will update the Nuke scene and return the state
            if restored_state is not None:
                for row in range(self.table.rowCount()):
                    node_name = self.table.item(row, 0).text()
                    if node_name in restored_state:
                        new_path = restored_state[node_name]
                        self.table.setItem(row, 3, QTableWidgetItem(new_path))
                self.update_tables()
            else:
                QMessageBox.warning(self, "Snapshot", f"Failed to load state for version {selected_version}.")

    def populate_saved_states_table(self, saved_versions):
        """Populates the saved states table.

        Adds rows for each version and sets the version name,
        checkbox, and paths string.
        """
        for row, version in enumerate(saved_versions):
            self.saved_states_table.setItem(row, 0, QTableWidgetItem(version))
            self.add_checkbox_to_table(self.saved_states_table, row, 1)  # Added checkbox in 'Select' column

            # Fetch the saved state for the current version
            saved_state = self.api.database.load_state(version)
            paths_text = "\n".join([f"{node_name} : {path}" for node_name, path in saved_state.items()])

            self.saved_states_table.setItem(row, 2, QTableWidgetItem(paths_text))  # Renamed to plural and reordered

    def create_snapshot(self):
        """Creates a snapshot.

        Captures selected nodes, generates a version, and saves
        via the API. Shows messages based on success/failure.
        """

        # Capture the selected nodes to create a snapshot
        selected_nodes = self.get_selected_snapshot_nodes()
        if not selected_nodes:
            QMessageBox.warning(self, "Snapshot", "No nodes selected")
            return

        # Generate a version for the current snapshot
        version = self.api.generate_version("timestamp")

        # Save the state for the selected nodes with the generated version
        success = self.api.save_state(version, selected_nodes)
        if success:
            self.snapshot_data.append(version)
            QMessageBox.information(self, "Snapshot", "State saved successfully!")
            self.update_saved_states_table()  # Reload the saved states table after saving a state
        else:
            QMessageBox.warning(self, "Snapshot", "Failed to save state.")

    def update_saved_states_table(self):
        """Updates the saved states table.

        Fetches saved versions, sets row count, and populates
        the table.
        """
        saved_versions = self.fetch_saved_versions()
        self.set_table_row_count(self.saved_states_table, len(saved_versions))
        self.populate_saved_states_table(saved_versions)

    def update_snapshot_table(self):
        """Updates the snapshot table.

        Gets snapshot nodes via API, sets row count, and
        populates the table.
        """
        snapshot_nodes = self.api.get_snapshot_nodes()
        self.set_table_row_count(self.snapshot_table, len(snapshot_nodes))
        self.populate_snapshot_table(snapshot_nodes)

    def fetch_saved_versions(self):
        return [state['version'] for state in self.api.get_saved_states_with_dates()]

    def toggle_edit_mode(self, state=None):
        if state is None:
            state = self.edit_mode_checkbox.checkState()
        print(f"toggle_edit_mode called with state: {state}")
        # Enable/Disable the Default and Regex tabs
        self.default_tab.setEnabled(not state)
        self.regex_tab.setEnabled(not state)
        # Make non-New Path columns read only
        for table in [self.table, self.snapshot_table, self.saved_states_table]:
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item is not None:  # Check if item exists
                        if col != 3:  # Make all columns except 'New Path' non-editable
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        else:  # Make 'New Path' editable based on the state of the checkbox
                            if state == Qt.Checked:
                                item.setFlags(item.flags() | Qt.ItemIsEditable)
                            else:
                                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    @staticmethod
    def set_table_row_count(table, count):
        table.setRowCount(count)

    def populate_snapshot_table(self, snapshot_nodes):
        for row, node in enumerate(snapshot_nodes):
            node_name = node.get('full_name', node.get('name', 'Unknown'))  # Fallback to 'name' or 'Unknown'
            self.snapshot_table.setItem(row, 0, QTableWidgetItem(node_name))
            self.add_checkbox_to_table(self.snapshot_table, row, 1)
            self.snapshot_table.setItem(row, 2, QTableWidgetItem(node.get('path', 'Unknown')))  # Fallback to 'Unknown'

    @staticmethod
    def add_checkbox_to_table(table, row, col):
        checkbox = QTableWidgetItem()
        checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox.setCheckState(Qt.Unchecked)
        table.setItem(row, col, checkbox)

    def remember_new_paths(self):
        new_paths = {}
        for row in range(self.table.rowCount()):
            node_name = self.table.item(row, 0).text()
            new_path = self.table.item(row, 3).text()
            new_paths[node_name] = new_path
        return new_paths

    @staticmethod
    def remember_checkbox_states(table):
        states = {}
        for row in range(table.rowCount()):
            node_name = table.item(row, 0).text()
            states[node_name] = table.item(row, 1).checkState()
        return states

    def update_main_table(self):
        nodes = self.api.get_all_read_nodes()
        self.set_table_row_count(self.table, len(nodes))
        for row, node in enumerate(nodes):
            self.table.setItem(row, 0, QTableWidgetItem(node['full_name']))
            self.add_checkbox_to_table(self.table, row, 1)
            self.table.setItem(row, 2, QTableWidgetItem(node['path']))
            self.table.setItem(row, 3, QTableWidgetItem(""))

    @staticmethod
    def restore_checkbox_states(table, states):
        for row in range(table.rowCount()):
            node_name = table.item(row, 0).text()
            if node_name in states:
                table.item(row, 1).setCheckState(states[node_name])

    def restore_new_paths(self, new_paths):
        for row in range(self.table.rowCount()):
            node_name = self.table.item(row, 0).text()
            if node_name in new_paths:
                self.table.setItem(row, 3, QTableWidgetItem(new_paths[node_name]))
            else:
                self.table.setItem(row, 3, QTableWidgetItem(""))

    def update_tables(self):
        new_paths = self.remember_new_paths()
        main_table_states = self.remember_checkbox_states(self.table)
        snapshot_table_states = self.remember_checkbox_states(self.snapshot_table)

        self.update_main_table()
        self.update_snapshot_table()
        self.update_saved_states_table()

        self.restore_checkbox_states(self.table, main_table_states)
        self.restore_checkbox_states(self.snapshot_table, snapshot_table_states)
        self.restore_new_paths(new_paths)

        self.toggle_edit_mode()

    def test_regex(self):
        regex_pattern = self.regex_pattern_field.text()
        test_string = self.regex_new_path_field.text()
        try:
            match = re.search(regex_pattern, test_string)
            if match:
                QMessageBox.information(self, "Regex Test", f"Pattern matches: {match.group()}")
            else:
                QMessageBox.warning(self, "Regex Test", "Pattern doesn't match.")
        except re.error:
            QMessageBox.critical(self, "Regex Test", "Invalid regex pattern.")

    def generate_new_path_with_regex(self):
        regex_pattern = self.regex_pattern_field.text()
        replacement_path = self.regex_new_path_field.text()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1).checkState() == Qt.Checked:
                current_path = self.table.item(row, 2).text()
                new_path = re.sub(regex_pattern, replacement_path, current_path)
                self.table.setItem(row, 3, QTableWidgetItem(new_path))

    def generate_new_path(self):
        # Get the matching path and replacement path from user input
        matching_path = self.matching_path_field.text()
        replacement_path = self.replacement_path_field.text()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1).checkState() == Qt.Checked:
                current_path = self.table.item(row, 2).text()
                # If the matching path is in the current path, replace it
                if matching_path in current_path:
                    new_path = current_path.replace(matching_path, replacement_path)
                    self.table.setItem(row, 3, QTableWidgetItem(new_path))

    def get_selected_snapshot_nodes(self):
        selected_nodes = []

        for row in range(self.snapshot_table.rowCount()):
            node_name = self.snapshot_table.item(row, 0).text()
            if self.snapshot_table.item(row, 1).checkState() == Qt.Checked:
                selected_nodes.append(node_name)

        return selected_nodes


if __name__ == "__main__":
    app = QApplication([])
    window = RelinkNukeGUI()
    window.show()
    app.exec_()
