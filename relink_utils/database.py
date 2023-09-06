"""
relink_database.py

Implements a SQLite database for storing relink history and node states.
"""

import json
from typing import Dict, List, Optional, Any
import os
import sqlite3


class RelinkDatabase:
    """
    A class that handles interactions with the relink history database.
    """

    def __init__(self, db_file=None):
        """Initialize the database connection.

                Args:
                    db_file: Path to the SQLite database file. Defaults to
                        relink_database.db in the package data directory.
        """
        if db_file is None:
            db_file = os.path.join(os.path.dirname(__file__), 'data', 'relink_database.db')
        self.db_file = db_file
        self.conn = None
        self.connect()
        self.create_table()

    def connect(self):
        """
        Establish a connection to the database.
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            print("Database connection established.")
        except sqlite3.Error as e:
            print("Error connecting to the database:", e)

    def create_table(self):
        """Create the relink history and saved states tables if needed."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS relink_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                old_path_regex TEXT,
                new_path TEXT,
                use_regex INTEGER,
                affected_nodes INTEGER
            );''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS saved_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE,
                state TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''')

            self.conn.commit()
            print("Tables created.")
        except sqlite3.Error as e:
            print("Error creating tables:", e)

    def get_saved_states_with_dates(self) -> List[Dict[str, str]]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT version, timestamp FROM saved_states")
            rows = cursor.fetchall()
            return [{"version": row[0], "date": row[1]} for row in rows]
        except sqlite3.Error as e:
            print("Error fetching saved states with dates:", e)
            return []

    def log_relink_operation(self, old_path_regex, new_path):
        """
        Log a relink operation to the database.

        Args:
            old_path_regex (str): The regex pattern for old paths.
            new_path (str): The new path.
        """
        # Insert the relink operation into the database
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO relink_history (old_path_regex, new_path)
                VALUES (?, ?);
            ''', (old_path_regex, new_path))
            self.conn.commit()
            print("History entry inserted.")
        except sqlite3.Error as e:
            print("Error inserting history entry:", e)

    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def save_state(self, version: str, state: Dict) -> bool:
        """
        Save the current state of all paths.

        Args:
            version (str): The version name for the state.
            state (Dict): The state to save.

        Returns:
            bool: True if the state was saved successfully, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO saved_states (version, state)
                VALUES (?, ?);
            ''', (version, json.dumps(state)))
            self.conn.commit()
            print(f"State {version} saved.")
            return True
        except sqlite3.Error as e:
            print("Error saving state:", e)
            return False

    def load_state(self, version: str) -> Optional[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT state FROM saved_states WHERE version = ?", (version,))
            row = cursor.fetchone()
            if row:
                loaded_state = json.loads(row[0])
                print(f"Successfully loaded state {version}.")
                return loaded_state
            else:
                print(f"No state found for version {version}.")
                return None
        except sqlite3.Error as e:
            print("Error loading state:", e)
            return None

    def get_saved_states(self) -> List[str]:
        """
        Get a list of all saved states.

        Returns:
            List[str]: The list of saved state versions.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT version FROM saved_states")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            print("Error fetching saved states:", e)
            return []

    def get_last_version(self) -> str:
        """
        Get the last saved version from the database.

        Returns:
            str: The last saved version or "0" if no versions are found.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT version FROM saved_states ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return "0"
        except sqlite3.Error as e:
            print("Error fetching the last version:", e)
            return "0"

    def state_exists(self, version: str) -> bool:
        """
        Check if a state with the given version exists in the database.

        Args:
            version (str): The version name for the state.

        Returns:
            bool: True if the state exists, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM saved_states WHERE version = ?", (version,))
            row = cursor.fetchone()
            return row[0] > 0
        except sqlite3.Error as e:
            print(f"Error checking if state exists: {e}")
            return False

