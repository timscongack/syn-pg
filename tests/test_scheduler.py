import unittest
from unittest.mock import patch, MagicMock
from src.scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    @patch("src.scheduler.BackgroundScheduler")
    @patch("src.scheduler.Database")
    @patch("src.scheduler.GPTQueryGenerator")
    @patch("src.scheduler.DataGenerator")
    def test_execute_process(
        self,
        MockDataGenerator: MagicMock,
        MockGPTQueryGenerator: MagicMock,
        MockDatabase: MagicMock,
        MockBackgroundScheduler: MagicMock,
    ):
        mock_db = MockDatabase.return_value
        mock_gpt = MockGPTQueryGenerator.return_value
        mock_data_generator = MockDataGenerator.return_value

        mock_db.get_all_ddl.return_value = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]
        mock_gpt.generate_queries.return_value = ["INSERT INTO test (id) VALUES (1);"]

        mock_cursor = MagicMock()
        mock_db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        scheduler = Scheduler()
        scheduler.db = mock_db
        scheduler.gpt = mock_gpt
        scheduler.data_generator = mock_data_generator

        scheduler.execute_process()

        mock_db.connect.assert_called_once()
        mock_db.close.assert_called_once()
        mock_cursor.execute.assert_any_call("INSERT INTO test (id) VALUES (1);")

    def test_parse_cron(self):
        scheduler = Scheduler()
        cron_params = scheduler.parse_cron("* * * * *")
        self.assertEqual(cron_params["minute"], "*")
        self.assertEqual(cron_params["hour"], "*")


if __name__ == "__main__":
    unittest.main()