import sys
import os
import sqlite3
import unittest
from unittest.mock import patch

from src import SystemMonitorApp


class TestSystemMonitorApp(unittest.TestCase):
    def setUp(self):
        self.db_file = "test_resource_usage.db"
        self.app = SystemMonitorApp(db_file=self.db_file)
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()
        self.app.destroy()
        if os.path.exists(self.app.db_file):
            os.remove(self.app.db_file)

    @patch("tkinter.messagebox.showerror")
    def test_invalid_input(self, mock_messagebox):
        self.app.interval_entry.insert(0, "Invalid input")
        self.app.set_update_interval()

        self.assertTrue(mock_messagebox.called)

    def test_database_insertion(self):
        cpu_usage = 10.0
        ram_usage = 10.0
        disk_usage = 10.0
        self.app.record_to_db(cpu_usage, ram_usage, disk_usage)
        self.cursor.execute(
            "SELECT cpu, ram, disk FROM usage ORDER BY timestamp DESC LIMIT 1"
        )
        data = self.cursor.fetchone()
        self.assertEqual(data, (cpu_usage, ram_usage, disk_usage))


if __name__ == "__main__":
    unittest.main()
