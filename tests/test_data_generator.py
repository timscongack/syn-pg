import unittest
from unittest.mock import patch, MagicMock
from src.data_generator import DataGenerator


class TestDataGenerator(unittest.TestCase):
    @patch("src.data_generator.Database")
    @patch("src.data_generator.GPTQueryGenerator")
    def test_generate_and_run_queries(self, MockGPTQueryGenerator: MagicMock, MockDatabase: MagicMock):
        """Test successful generation and execution of queries."""
        mock_db = MockDatabase.return_value
        mock_gpt = MockGPTQueryGenerator.return_value
        mock_cursor = MagicMock()
        mock_db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_db.get_all_ddl.return_value = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]
        mock_gpt.generate_queries.return_value = ["INSERT INTO test (id) VALUES (1);"]

        generator = DataGenerator(mock_db)
        generator.generate_and_run_queries()

        mock_db.connect.assert_called_once()
        mock_db.close.assert_called_once()
        mock_cursor.execute.assert_any_call("BEGIN;")
        mock_cursor.execute.assert_any_call("INSERT INTO test (id) VALUES (1);")
        mock_cursor.execute.assert_any_call("COMMIT;")

    @patch("src.data_generator.Database")
    @patch("src.data_generator.GPTQueryGenerator")
    def test_handle_query_failure(self, MockGPTQueryGenerator: MagicMock, MockDatabase: MagicMock):
        """Test handling of query execution failure."""
        mock_db = MockDatabase.return_value
        mock_gpt = MockGPTQueryGenerator.return_value
        mock_cursor = MagicMock()
        mock_db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_db.get_all_ddl.return_value = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]
        mock_gpt.generate_queries.return_value = ["INSERT INTO test (id) VALUES (1);"]
        mock_cursor.execute.side_effect = [None, Exception("Execution failed"), None]

        generator = DataGenerator(mock_db)
        generator.generate_and_run_queries()

        mock_db.connect.assert_called_once()
        mock_cursor.execute.assert_any_call("BEGIN;")
        mock_cursor.execute.assert_any_call("INSERT INTO test (id) VALUES (1);")
        mock_db.connection.rollback.assert_called_once()
        mock_db.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()