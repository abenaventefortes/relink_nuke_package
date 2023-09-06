"""
Module for performing environment checks.

This module provides classes for checking if the Python and Nuke
environments meet the requirements for the application.

"""

import sys  # Import sys module


class EnvironmentChecker:
    """Base class for environment checkers."""

    def check(self):
        """
        Checks if the environment meets the requirements.

        Raises:
            NotImplementedError: This method should be overridden.

        Returns:
            bool: True if the environment passes the check, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclass")


class PythonEnvironmentChecker(EnvironmentChecker):
    """Checker for Python environment."""

    def check(self):  # Implement check method
        """
        Checks if the Python version is 3.9+.

        Returns:
            bool: True if Python version is 3.9+, False otherwise.
        """
        return sys.version_info[0] == 3 and sys.version_info[1] >= 9  # Check Python version


class NukeEnvironmentChecker(EnvironmentChecker):
    """Checker for Nuke environment."""

    def check(self):  # Implement check method
        """
        Checks if Nuke version is 14.0v5.

        Returns:
            bool: True if Nuke version is 14.0v5, False otherwise.
        """

        try:
            import nuke  # Import nuke
            nuke_version = nuke.NUKE_VERSION_STRING  # Get Nuke version
            return nuke_version == '14.0v5'  # Check if version matches
        except ImportError:
            return False


class EnvironmentCheckFactory:
    """
    Factory class for creating environment checkers.
    """

    @staticmethod
    def create_checker(checker_type):  # Factory method
        """
        Creates the environment checker object.

        Args:
            checker_type (str): Type of checker to create ('Python' or 'Nuke')

        Returns:
            EnvironmentChecker: Instance of the checker class.

        Raises:
            ValueError: If unsupported checker type is specified.
        """

        if checker_type == 'Python':
            return PythonEnvironmentChecker()
        elif checker_type == 'Nuke':
            return NukeEnvironmentChecker()
        else:
            raise ValueError(f"Unsupported checker type: {checker_type}")
