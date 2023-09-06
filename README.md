# Relink Utils

This package contains utility modules and scripts for the Relink Nuke Plugin Installer.

## Structure

The package structure is as follows:
relink_utils/
    __init__.py
    api.py
    checks.py
    database.py
    gui.py
    installation.md
    install_script.py
    logs/
        relink.log
    nuke_menu/
        menu.py
    README.md
    requirements.txt
    setup.py
    testing.md
    utils/
        __init__.py
    data/
        relink_database.db
## Modules

-  `api.py` : Contains classes and functions for the Relink Nuke Plugin API.
-  `checks.py` : Contains functions for performing various checks and validations.
-  `database.py` : Contains classes and functions for interacting with the Relink database.
-  `gui.py` : Contains classes and functions for the GUI components of the Relink Nuke Plugin Installer.
-  `install_script.py` : Contains the main installation script for the Relink Nuke Plugin Installer.
-  `menu.py` : Contains the menu file for the Relink Nuke Plugin.
-  `README.md` : This file, providing an overview of the Relink Utils package.
-  `requirements.txt` : Contains the required dependencies for the Relink Nuke Plugin Installer.
-  `setup.py` : Contains the setup configuration for the Relink Nuke Plugin Installer.
-  `testing.md` : Contains information about testing the Relink Nuke Plugin Installer.
-  `utils/` : A package containing utility modules for the Relink Nuke Plugin Installer.
-  `data/` : Contains the Relink database file.
-  `logs/` : Contains the log file for the Relink Nuke Plugin Installer.

## Installation

To install the Relink Nuke Plugin Installer, follow these steps:

1. Make sure you have Python 3.x installed on your system.
2. Clone or download the Relink Utils package from the GitHub repository.
3. Open a command prompt or terminal and navigate to the root directory of the Relink Utils package.
4. Run the following command to install the required dependencies:
pip install -r requirements.txt
5. Once the dependencies are installed, you can proceed with running the installation script or using the Relink Nuke Plugin API.

For more detailed installation instructions and usage guidelines, refer to the  `installation.md`  and  `api.md`  files respectively.

## Testing

To run the unit tests for the Relink Nuke Plugin Installer, follow these steps:

1. Make sure you have installed the required dependencies as mentioned in the installation instructions.
2. Open a command prompt or terminal and navigate to the root directory of the Relink Utils package.
3. Run the following command to execute the unit tests:
python -m unittest discover -s tests -p "test_*.py"
This will discover and run all the unit tests in the  `tests`  directory.

For more information about testing the Relink Nuke Plugin Installer, refer to the  `testing.md`  file.

## License

This package is licensed under the MIT License. See the  `LICENSE.md`  file for more details.