import unittest
from unittest.mock import patch, MagicMock
from src.data_generator import DataGenerator

class TestDataGenerator(unittest.TestCase):
    @patch("src.data_generator.Database")
    @patch("src.data_generator.GPTQueryGenerator")
    def test_generate_and_run_queries(self, MockGPTQueryGenerator: MagicMock, MockDatabase: MagicMock):
        mock_db = MockDatabase.return_value
        mock_gpt = MockGPTQueryGenerator.return_value
        mock_db.get_all_ddl.return_value = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]
        mock_gpt.generate_queries.return_value = ["INSERT INTO test (id) VALUES (1);"]

        generator = DataGenerator(mock_db)
        generator.generate_and_run_queries()

        mock_db.connect.assert_called_once()
        mock_db.close.assert_called_once()
        mock_db.connection.cursor.return_value.execute.assert_any_call("INSERT INTO test (id) VALUES (1);")

    @patch("src.data_generator.Database")
    def test_handle_query_failure(self, MockDatabase: MagicMock):
        mock_db = MockDatabase.return_value
        mock_db.get_all_ddl.return_value = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]

        generator = DataGenerator(mock_db)
        generator.generate_and_run_queries()

        mock_db.connection.rollback.assert_called()


if __name__ == "__main__":
    unittest.main()