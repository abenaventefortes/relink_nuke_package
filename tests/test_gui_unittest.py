import unittest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem
from relink_utils import RelinkNukeGUI


class TestRelinkNukeGUI(unittest.TestCase):

    def setUp(self):
        self.gui = RelinkNukeGUI()

    def test_handle_item_changed_checked(self):
        item = QTableWidgetItem()
        item.setCheckState(Qt.Checked)
        item.setRow(0)
        item.setColumn(1)
        self.gui.handle_item_changed(item)
        self.assertEqual(self.gui.node_states["Node1"], "selected")

    def test_handle_item_changed_unchecked(self):
        item = QTableWidgetItem()
        item.setCheckState(Qt.Unchecked)
        item.setRow(0)
        item.setColumn(1)
        self.gui.handle_item_changed(item)
        self.assertEqual(self.gui.node_states["Node1"], "unselected")

    def test_get_selected_snapshot_nodes(self):
        item1 = QTableWidgetItem()
        item1.setCheckState(Qt.Checked)
        item1.setText("Node1")
        item2 = QTableWidgetItem()
        item2.setCheckState(Qt.Unchecked)
        item2.setText("Node2")
        self.gui.snapshot_table.setItem(0, 0, item1)
        self.gui.snapshot_table.setItem(1, 0, item2)
        selected_nodes = self.gui.get_selected_snapshot_nodes()
        self.assertEqual(selected_nodes, ["Node1"])

    def test_get_selected_snapshot_version(self):
        item1 = QTableWidgetItem()
        item1.setCheckState(Qt.Checked)
        item1.setText("Version1")
        item2 = QTableWidgetItem()
        item2.setCheckState(Qt.Unchecked)
        item2.setText("Version2")
        self.gui.saved_states_table.setItem(0, 0, item1)
        self.gui.saved_states_table.setItem(1, 0, item2)
        selected_version = self.gui.get_selected_snapshot_version()
        self.assertEqual(selected_version, "Version1")


if __name__ == '__main__':
    unittest.main()
