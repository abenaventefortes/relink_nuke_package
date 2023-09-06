import sys
from setuptools import setup, find_packages

# Check Python version
python_version = sys.version_info
if python_version < (3, 9) or python_version >= (3, 10):
    sys.exit("""
Error: This package requires Python 3.9.x.
You are using Python {}.{}.{}.

To install Python 3.9.x, you can do one of the following:

1. From Python's official site:
    - Download the installer for Python 3.9.x from https://www.python.org/downloads/
    - Follow the installation instructions.

2. Using package manager (Ubuntu example):
    $ sudo apt update
    $ sudo apt install python3.9

After installing the correct Python version, try running pip install again.
""".format(*python_version))

# Setup configuration
setup(
    name="relink-nuke-package",
    version="1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'relink_nuke=relink_utils.cli:main',
            'relink_nuke_plugin=relink_utils.install_script:main'
        ],
    },
    package_data={
        'relink_utils': ['data/*', 'logs/*', 'install_script.py']
    },
    python_requires='~=3.9.0'  # Only allow Python 3.9.x
)
