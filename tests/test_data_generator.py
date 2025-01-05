import unittest
from unittest.mock import MagicMock, patch
from .db import Database
from .data_generator import DataGenerator

class TestDataGenerator(unittest.TestCase):
    @patch(".data_generator.GPTQueryGenerator")
    @patch(".data_generator.Database")
    def test_generate_and_run_queries(self, MockDatabase, MockGPTQueryGenerator):
        mock_db = MockDatabase.return_value
        mock_db.get_all_ddl.return_value = ["CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));"]
        mock_db.connection = MagicMock()
        mock_gpt = MockGPTQueryGenerator.return_value
        mock_gpt.generate_queries.return_value = [
            "INSERT INTO users (id, name) VALUES (1, 'Alice');",
            "INSERT INTO users (id, name) VALUES (2, 'Bob');"
        ]
        data_generator = DataGenerator(mock_db)
        data_generator.generate_and_run_queries()
        cur = mock_db.connection.cursor.return_value.__enter__.return_value
        cur.execute.assert_any_call("BEGIN;")
        cur.execute.assert_any_call("INSERT INTO users (id, name) VALUES (1, 'Alice');")
        cur.execute.assert_any_call("COMMIT;")
        cur.execute.assert_any_call("INSERT INTO users (id, name) VALUES (2, 'Bob');")
        self.assertEqual(cur.execute.call_count, 6)
        mock_db.connection.rollback.assert_not_called()

    @patch(".data_generator.GPTQueryGenerator")
    @patch(".data_generator.Database")
    def test_generate_and_run_queries_with_failure(self, MockDatabase, MockGPTQueryGenerator):
        mock_db = MockDatabase.return_value
        mock_db.get_all_ddl.return_value = ["CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));"]
        mock_db.connection = MagicMock()
        mock_gpt = MockGPTQueryGenerator.return_value
        mock_gpt.generate_queries.return_value = [
            "INSERT INTO users (id, name) VALUES (1, 'Alice');",
            "INVALID SQL QUERY;",
            "INSERT INTO users (id, name) VALUES (2, 'Bob');"
        ]
        cur = mock_db.connection.cursor.return_value.__enter__.return_value
        cur.execute.side_effect = [None, Exception("Syntax error"), None]
        data_generator = DataGenerator(mock_db)
        data_generator.generate_and_run_queries()
        mock_db.connection.rollback.assert_called_once()
        self.assertGreaterEqual(cur.execute.call_count, 6)