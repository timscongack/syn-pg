import unittest
from unittest.mock import patch, MagicMock
from src.db import Database


class TestDatabase(unittest.TestCase):
    @patch("src.db.psycopg2.connect")
    def test_connect_successful(self, mock_connect: MagicMock):
        db = Database()
        db.connect()
        mock_connect.assert_called_once_with(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.database,
        )
        self.assertIsNotNone(db.connection)

    @patch("src.db.psycopg2.connect", side_effect=Exception("Connection error"))
    def test_connect_failure(self, mock_connect: MagicMock):
        db = Database()
        with self.assertRaises(ConnectionError):
            db.connect()

    @patch("src.db.psycopg2.connect")
    def test_get_all_ddl(self, mock_connect: MagicMock):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.side_effect = [
            [("CREATE TABLE test_table (id integer, name text);",)],
            [("CREATE VIEW sample_view AS SELECT * FROM test_table;",)]
        ]

        db = Database()
        db.connect()
        ddl_statements = db.get_all_ddl()

        expected = [
            "CREATE TABLE test_table (id integer, name text);",
            "CREATE VIEW sample_view AS SELECT * FROM test_table;"
        ]
        self.assertEqual(ddl_statements, expected)

    @patch("src.db.psycopg2.connect")
    def test_close_connection(self, mock_connect: MagicMock):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = Database()
        db.connect()
        db.close()
        mock_connection.close.assert_called_once()

    @patch("src.db.psycopg2.connect")
    def test_close_no_active_connection(self, mock_connect: MagicMock):
        db = Database()
        with self.assertLogs(level="INFO") as log:
            db.close()
        self.assertIn("No active database connection to close.", log.output[0])


if __name__ == "__main__":
    unittest.main()