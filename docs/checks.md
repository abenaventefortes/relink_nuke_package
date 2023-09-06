# Environment Checks

This module provides classes for checking if the Python and Nuke environments meet the requirements of the application.

## Overview

The key components are:

-  `EnvironmentChecker`  - Base class for checkers
-  `PythonEnvironmentChecker`  - Checks Python version 
-  `NukeEnvironmentChecker`  - Checks Nuke version
-  `EnvironmentCheckFactory`  - Creates checkers

To use:

1. Create a checker object via the factory
2. Call the  `check()`  method to run the check

## Checkers

The available checkers are:

### PythonEnvironmentChecker

Checks that the Python version is 3.9+

Usage:
checker = EnvironmentCheckFactory.create_checker('Python')
result = checker.check()
### NukeEnvironmentChecker 

Checks that the Nuke version is 14.0v5

Usage:
checker = EnvironmentCheckFactory.create_checker('Nuke')
result = checker.check()
## Factory

The  `EnvironmentCheckFactory`  creates checker instances:
checker = EnvironmentCheckFactory.create_checker('Python')
It takes the checker type as a string, e.g. 'Python' or 'Nuke'.

## Exceptions

-  `NotImplementedError`  - Base class check() method not implemented
-  `ImportError`  - Nuke library not available
-  `ValueError`  - Invalid checker type provided
