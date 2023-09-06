import sys
import argparse
import os
import re
import shutil
from difflib import unified_diff
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QCheckBox, \
    QMessageBox, QTextEdit, QSizePolicy

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

PLACEHOLDER_LINE = "# sys.path.append('your_package_root_path_here')"


def get_dark_theme():
    """
    Returns a dark theme stylesheet for PyQt5 widgets.

    Returns:
        str: The stylesheet string.
    """
    return """
    QWidget {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    QPushButton {
        background-color: #555555;
        border: 1px solid #2E2E2E;
    }
    QPushButton:hover {
        background-color: #888888;
    }
    QLineEdit {
        background-color: #555555;
        border: 1px solid #2E2E2E;
    }
    QLabel {
        color: #FFFFFF;
    }
    """


class Signal(QObject):
    """
    Defines signals for PyQt5.
    """
    restore_backup_signal = pyqtSignal(str, str)


class InstallerBase:
    """
    Base class for Installer, contains utility methods for file operations.
    """
    @staticmethod
    def get_next_backup_version(file_path):
        """
        Get the next backup version for a given file path.

        Args:
            file_path (str): The file path to backup.

        Returns:
            str: The next backup file name.
        """
        version = 0
        while True:
            backup_name = f"{file_path}.bckp_ver{str(version).zfill(2)}"
            if not os.path.exists(backup_name):
                return backup_name
            version += 1

    @staticmethod
    def create_backup(file_path):
        """
        Create a backup of the given file.

        Args:
            file_path (str): The file path to backup.
        """
        backup_name = InstallerBase.get_next_backup_version(file_path)
        if os.path.exists(file_path):
            shutil.copyfile(file_path, backup_name)
            print(f"Backup created: {backup_name}")
        else:
            print(f"No file to backup at {file_path}")

    @staticmethod
    def insert_sys_path_line(menu_file_path, sys_path_line):
        """
        Insert a sys.path line into the menu file if it doesn't already exist.

        Args:
            menu_file_path (str): The path to the menu file.
            sys_path_line (str): The sys.path line to insert.
        """
        with open(menu_file_path, 'r') as f:
            content = f.read()
        if sys_path_line not in content:
            with open(menu_file_path, 'a') as f:
                f.write(sys_path_line)

    @staticmethod
    def read_menu_file(file_path):
        """
        Read the content of a menu file.

        Args:
            file_path (str): The path to the menu file.

        Returns:
            str: The content of the menu file.
        """
        with open(file_path, 'r') as f:
            return f.read()


class UserChoiceHandler:
    """
    Abstract class for handling user choices.
    """
    def get_user_choice(self, prompt):
        """
        Get the user's choice.

        Args:
            prompt (str): The prompt to display to the user.

        Returns:
            str: The user's choice.

        Raises:
            NotImplementedError: This method should be overridden by subclass.
        """
        raise NotImplementedError("This method should be overridden by subclass.")


class CLIHandler(UserChoiceHandler):
    """
    Command-line interface handler for user choices.
    """
    def get_user_choice(self, prompt):
        """
        Get the user's choice via the command line.

        Args:
            prompt (str): The prompt to display to the user.

        Returns:
            str: The user's choice.
        """
        return input(prompt)


class Installer(QWidget, InstallerBase):
    """
    Installer class for the Relink Nuke Plugin Installer.

    Attributes:
        choice_handler (UserChoiceHandler): Object to handle user choices.
        menu_file_src (str): Source path for the menu file.
        menu_path_input (QLineEdit): Input field for the menu path.
    """

    def __init__(self, choice_handler, menu_file_src):
        """
        Initialize the Installer object.

        Args:
            choice_handler (UserChoiceHandler): Object to handle user choices.
            menu_file_src (str): Source path for the menu file.
        """
        super().__init__()
        self.choice_handler = choice_handler
        self.menu_file_src = menu_file_src  # Store the menu_file_src as an instance attribute

        # Initialize UI components
        layout = QVBoxLayout()
        self.label = QLabel("Welcome to Relink Nuke Plugin Installer")
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Enter path for menu.py or leave empty for default")
        self.browseButton = QPushButton("Browse")
        self.checkBox = QCheckBox("Create Backup")
        self.checkBox.setChecked(True)  # Set to true by default
        self.installButton = QPushButton("Install Relink Nuke Plugin Installer to Default Home Directory")
        self.restoreButton = QPushButton("Restore Backup")

        # Add UI components to layout
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.checkBox)
        layout.addWidget(self.installButton)
        layout.addWidget(self.restoreButton)

        # Set layout and stylesheet
        self.setLayout(layout)
        self.setStyleSheet(get_dark_theme())

        # Connect signals to slots
        self.browseButton.clicked.connect(self.browse)
        self.installButton.clicked.connect(self.install_menu)
        self.restoreButton.clicked.connect(self.restore_backup)
        self.lineEdit.textChanged.connect(self.update_install_button_label)

        # Store menu_path_input as an instance attribute
        self.menu_path_input = self.lineEdit

    @staticmethod
    def replace_placeholder(menu_file_path, sys_path_line):
        """
        Replace the placeholder line in the menu file with the actual sys.path line.

        Args:
            menu_file_path (str): Path to the menu file.
            sys_path_line (str): The sys.path line to insert.
        """
        placeholder = "# sys.path.append('your_package_root_path_here')"
        with open(menu_file_path, 'r+') as f:
            content = f.read()
            content = content.replace(placeholder, sys_path_line)
            f.seek(0)
            f.write(content)
            f.truncate()

    def update_install_button_label(self):
        """
        Update the label of the installation button based on the content of the line edit.
        """
        if self.lineEdit.text():
            self.installButton.setText("Install Relink Nuke Plugin Installer to Custom Path")
        else:
            self.installButton.setText("Install Relink Nuke Plugin Installer to Default Home Directory")

    def browse(self):
        """
        Open a directory selection dialog and update the line edit with the selected path.
        """
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.lineEdit.setText(folder)

    def show_diff(self, existing_menu_file_path, new_menu_file_path):
        """Show the difference between the existing and new menu files.

        Args:
            existing_menu_file_path (str): Path to the existing menu file.
            new_menu_file_path (str): Path to the new menu file.
        """
        existing_menu_content = self.read_menu_file(existing_menu_file_path)
        new_menu_content = self.read_menu_file(new_menu_file_path)

        # Generate the unified diff
        diff = list(unified_diff(existing_menu_content.splitlines(), new_menu_content.splitlines(), lineterm=""))
        diff_text = "\n".join(diff)

        print("Showing diff in terminal:")
        print(diff_text)

        # Create and configure QMessageBox for showing the diff
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Diff Viewer")
        label = QLabel("The following diff has been found:")
        label.setAlignment(Qt.AlignCenter)
        text_edit = QTextEdit()
        text_edit.setPlainText(diff_text)
        text_edit.setReadOnly(True)  # Make it read-only
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_edit.setMinimumSize(550, 350)
        msg_box.layout().addWidget(label)
        msg_box.layout().addWidget(text_edit)
        msg_box.addButton(QPushButton('Ok'), QMessageBox.YesRole)
        msg_box.resize(600, 400)  # Set the size of the dialog
        msg_box.exec_()

    @staticmethod
    def validate_path(path):
        """Validate the given path.

        Args:
            path (str): The path to validate.

        Raises:
            ValueError: If the path is invalid.
        """
        if not path:
            path = path.get_default_nuke_directory()
        if not os.path.isdir(path):
            raise ValueError("Invalid path")

    def install_menu(self):
        """
        Install the menu to the specified or default directory.
        """
        menu_path = self.lineEdit.text()
        if not menu_path:
            menu_path = self.get_default_nuke_directory()

        self.validate_path(menu_path)

        menu_file_dest = os.path.join(menu_path, 'menu.py')
        sys_path_line = f"sys.path.append(r'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}')\n"

        if os.path.exists(menu_file_dest):
            print("Existing menu.py found.")
            self.handle_existing_menu(menu_path, sys_path_line)
        else:
            print("No existing menu.py found. Copying...")
            shutil.copyfile(self.menu_file_src, menu_file_dest)
            self.replace_placeholder(menu_file_dest, sys_path_line)

    @staticmethod
    def insert_sys_path(menu_file_path, sys_path_line):
        """
        Insert the sys_path_line into the menu file if it doesn't already exist.

        Args:
            menu_file_path (str): The path to the menu file.
            sys_path_line (str): The line to insert.
        """
        with open(menu_file_path, 'r+') as f:
            content = f.read()
            if sys_path_line not in content:
                f.write(sys_path_line)  # Insert the sys_path_line

    def handle_existing_menu(self, menu_path, sys_path_line):
        """
        Handle the case where a menu.py file already exists.

        Args:
            menu_path (str): The path to the existing menu.
            sys_path_line (str): The sys path line to insert or replace.
        """
        menu_file_path = os.path.join(menu_path, 'menu.py')

        # Create a backup if the checkbox is checked
        if self.checkBox.isChecked():
            self.create_backup(menu_file_path)

        # Get user choice for how to handle existing menu.py
        choice = self.choice_handler.get_user_choice("menu.py exists. Replace(r), merge(m), or diff(d)?")

        if choice == 'r':
            print("Replacing existing menu.py...")
            shutil.copyfile(self.menu_file_src, menu_file_path)
            self.replace_placeholder(menu_file_path, sys_path_line)  # Make sure to call this method
        elif choice == 'm':
            print("Merging with existing menu.py...")
            self.merge_menu_files(menu_file_path, self.menu_file_src)
            self.replace_placeholder(menu_file_path, sys_path_line)  # Make sure to call this method
        elif choice == 'd':
            print("Showing diff...")
            self.show_diff(menu_file_path, self.menu_file_src)

    @staticmethod
    def merge_menu_files(existing_file_path, new_file_path):
        """
        Merge the existing and new menu files.

        Args:
            existing_file_path (str): The path to the existing file.
            new_file_path (str): The path to the new file.
        """
        with open(existing_file_path, 'r') as f1, open(new_file_path, 'r') as f2:
            existing_content = f1.read()
            new_content = f2.read()

        existing_lines = set(existing_content.split('\n'))
        new_lines = set(new_content.split('\n'))

        # Find lines that are in the new file but not in the existing file
        lines_to_add = new_lines - existing_lines
        lines_to_add_text = "\n".join(lines_to_add)

        # Merge and write back to the existing file
        merged_content = existing_content + "\n" + lines_to_add_text
        with open(existing_file_path, 'w') as f:
            f.write(merged_content)

    def restore_backup(self):
        """
        Restore the menu file from a backup.
        """
        menu_path = self.lineEdit.text() or self.get_default_nuke_directory()
        menu_file_path = os.path.join(menu_path, 'nuke_menu/menu.py')

        # If the specified path doesn't exist or there's no menu.py file, show a warning and return
        if not os.path.exists(menu_path) or not os.path.exists(menu_file_path):
            QMessageBox.warning(self, 'Error', 'Cannot find the menu.py file in the specified path.')
            return

        # Fetch all the backup files and sort them to get the latest
        backup_files = [f for f in os.listdir(menu_path) if re.match(r"menu\.py\.bckp_ver\d+", f)]
        backup_files.sort(reverse=True)

        # Use the latest backup or default to 'menu.py.bak' if no versioned backups are found
        backup_file = backup_files[0] if backup_files else 'menu.py.bak'
        backup_file_path = os.path.join(menu_path, backup_file)

        if os.path.exists(backup_file_path):
            shutil.copyfile(backup_file_path, menu_file_path)
            QMessageBox.information(self, 'Success', f'Successfully restored {menu_file_path} from {backup_file_path}.')
        else:
            QMessageBox.warning(self, 'Error', f'Cannot find a backup file in {menu_path}.')

    @staticmethod
    def get_default_nuke_directory() -> object:
        """
        Get the default Nuke directory based on the operating system.

        Returns:
            str: The default Nuke directory.
        """
        if sys.platform.startswith("win"):
            return os.path.expanduser(r"~\.nuke")
        elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            return os.path.expanduser("~/.nuke")
        else:
            return ""


class GUIHandler(UserChoiceHandler):
    """
    GUIHandler is a subclass of UserChoiceHandler that provides a GUI-based mechanism
    for getting user choices. It displays a message box with buttons for the user to
    select their choice.

    Attributes:
        None

    Methods:
        get_user_choice(prompt: str) -> str:
            Display a message box to get the user's choice.
    """
    def get_user_choice(self, prompt):
        """
        Display a message box to get the user's choice.

        Args:
            prompt (str): The prompt message to display.

        Returns:
            str: The user's choice ('r', 'm', 'd', or None).
        """
        msg_box = QMessageBox()
        msg_box.setText(prompt)

        replace_button = QPushButton('Replace (r)')
        merge_button = QPushButton('Merge (m)')
        diff_button = QPushButton('Diff (d)')

        msg_box.addButton(replace_button, QMessageBox.YesRole)
        msg_box.addButton(merge_button, QMessageBox.NoRole)
        msg_box.addButton(diff_button, QMessageBox.RejectRole)

        msg_box.exec_()

        clicked_button = msg_box.clickedButton()
        if clicked_button == replace_button:
            return 'r'
        elif clicked_button == merge_button:
            return 'm'
        elif clicked_button == diff_button:
            return 'd'
        else:
            return None


def install_with_gui():
    """
    Initialize and run the GUI-based installer.
    """
    # Create QApplication
    app = QApplication(sys.argv)
    app.setStyleSheet(get_dark_theme())  # Apply the dark theme to the entire application

    # Create GUI handler
    choice_handler = GUIHandler()

    # Get menu file source
    menu_file_src = os.path.join(os.path.dirname(__file__), "nuke_menu/menu.py")

    # Create Installer after QApplication
    installer = Installer(choice_handler, menu_file_src)
    installer.show()  # Show the installer GUI

    # Start event loop
    sys.exit(app.exec_())


def main():
    """
    Entry point for the application. Handles both CLI and GUI modes.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description="Install Relink Nuke Plugin")
    parser.add_argument("--menu", action="store_true", help="Install Relink Plugin Menu Bar")
    parser.add_argument("--file", help="Main file path")
    parser.add_argument("--backup", help="Backup file path")
    parser.add_argument("--restore", action="store_true", help="Restore backup")
    args = parser.parse_args()

    # Check if any CLI args passed
    if args.menu or args.file or args.backup or args.restore:
        # Create CLI handler
        choice_handler = CLIHandler()

        # Create Installer instance
        installer = Installer(choice_handler)

        # Handle menu arg
        if args.menu:
            menu_path = input(
                "Enter the path for menu.py (leave empty for default): ") or installer.get_default_nuke_directory()

            # Create a backup before any operations
            backup_enabled = input("Create backup? (y/n): ").lower() == 'y'
            if backup_enabled:
                InstallerBase.create_backup(os.path.join(menu_path, 'nuke_menu/menu.py'))

            installer.handle_existing_menu(menu_path)
    else:
        # No CLI args, call GUI
        install_with_gui()


if __name__ == "__main__":
    main()
