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
    def test_get_table_columns(self, mock_connect: MagicMock):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("id", "integer"), ("name", "text")]

        db = Database()
        db.connect()
        columns = db.get_table_columns("test_table")
        self.assertEqual(columns, [("id", "integer"), ("name", "text")])
        mock_cursor.execute.assert_called_once_with(
            "SELECT column_name, data_type "
            "FROM information_schema.columns "
            "WHERE table_name = %s AND table_schema = 'public';",
            ("test_table",),
        )

    @patch("src.db.psycopg2.connect")
    def test_get_all_table_columns(self, mock_connect: MagicMock):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("test_table", "id", "integer"),
            ("test_table", "name", "text"),
            ("another_table", "created_at", "timestamp"),
        ]

        db = Database()
        db.connect()
        table_columns = db.get_all_table_columns()
        expected = {
            "test_table": [
                {"column_name": "id", "data_type": "integer"},
                {"column_name": "name", "data_type": "text"},
            ],
            "another_table": [
                {"column_name": "created_at", "data_type": "timestamp"},
            ],
        }
        self.assertEqual(table_columns, expected)
        mock_cursor.execute.assert_called_once_with(
            "SELECT table_name, column_name, data_type "
            "FROM information_schema.columns "
            "WHERE table_schema = 'public';"
        )

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