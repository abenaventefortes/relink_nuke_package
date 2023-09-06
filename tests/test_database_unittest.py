import unittest
import sqlite3
from relink_utils.database import RelinkDatabase


class RelinkDatabaseTestCase(unittest.TestCase):

    def setUp(self):
        # Create a temporary in-memory database for testing
        self.conn = sqlite3.connect(':memory:')
        self.db = RelinkDatabase(db_file=':memory:')
        self.db.conn = self.conn

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_log_relink(self):
        old_path_regex = 'old/path/regex'
        new_path = 'new/path'
        self.db.log_relink(old_path_regex, new_path)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM relink_history")
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[2], old_path_regex)
        self.assertEqual(row[3], new_path)

    def test_save_state(self):
        version = 'v1.0'
        state = {'key': 'value'}
        self.assertTrue(self.db.save_state(version, state))

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM saved_states")
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[1], version)
        self.assertEqual(row[2], '{"key": "value"}')

    def test_load_state(self):
        version = 'v1.0'
        state = {'key': 'value'}
        self.db.save_state(version, state)

        loaded_state = self.db.load_state(version)

        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state, state)

    def test_get_saved_states(self):
        self.db.save_state('v1.0', {'key': 'value1'})
        self.db.save_state('v2.0', {'key': 'value2'})

        saved_states = self.db.get_saved_states()

        self.assertEqual(saved_states, ['v1.0', 'v2.0'])

    def test_get_last_version(self):
        self.db.save_state('v1.0', {'key': 'value1'})
        self.db.save_state('v2.0', {'key': 'value2'})

        last_version = self.db.get_last_version()

        self.assertEqual(last_version, 'v2.0')

    def test_state_exists(self):
        self.db.save_state('v1.0', {'key': 'value'})

        self.assertTrue(self.db.state_exists('v1.0'))
        self.assertFalse(self.db.state_exists('v2.0'))


if __name__ == '__main__':
    unittest.main()