import unittest
from unittest.mock import patch, MagicMock
from .db import Database

class TestDatabase(unittest.TestCase):
    @patch("psycopg2.connect")
    def test_connect(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = Database()
        db.connect()
        mock_connect.assert_called_once_with(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.database
        )
        self.assertEqual(db.connection, mock_connection)

    @patch("psycopg2.connect")
    def test_get_all_ddl(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = [("users", "CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));")]
        mock_connect.return_value = mock_connection
        db = Database()
        db.connect()
        ddl = db.get_all_ddl()
        mock_cursor.execute.assert_called_once_with(
            """
            SELECT relname, pg_catalog.pg_get_tabledef(oid)
            FROM pg_catalog.pg_class
            WHERE relkind = 'r' AND relnamespace IN (
                SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = 'public'
            );
            """
        )
        self.assertEqual(ddl, ["CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));"])

    @patch("psycopg2.connect")
    def test_close(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = Database()
        db.connect()
        db.close()
        mock_connection.close.assert_called_once()