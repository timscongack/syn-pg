import unittest
from unittest.mock import patch, MagicMock
from .scheduler import Scheduler

class TestScheduler(unittest.TestCase):
    @patch(".scheduler.BackgroundScheduler")
    @patch(".scheduler.Database")
    @patch(".scheduler.GPTQueryGenerator")
    @patch(".scheduler.DataGenerator")
    def test_execute_process(self, MockDataGenerator, MockGPTQueryGenerator, MockDatabase, MockScheduler):
        mock_db = MockDatabase.return_value
        mock_db.get_all_ddl.return_value = ["CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));"]
        mock_gpt = MockGPTQueryGenerator.return_value
        mock_gpt.generate_queries.return_value = [
            "INSERT INTO users (id, name) VALUES (1, 'Alice');",
            "INSERT INTO users (id, name) VALUES (2, 'Bob');"
        ]
        mock_cur = mock_db.connection.cursor.return_value.__enter__.return_value
        scheduler = Scheduler()
        scheduler.db = mock_db
        scheduler.gpt = mock_gpt
        scheduler.execute_process()
        mock_cur.execute.assert_any_call("BEGIN;")
        mock_cur.execute.assert_any_call("INSERT INTO users (id, name) VALUES (1, 'Alice');")
        mock_cur.execute.assert_any_call("COMMIT;")
        mock_cur.execute.assert_any_call("INSERT INTO users (id, name) VALUES (2, 'Bob');")
        mock_db.connection.rollback.assert_not_called()

    def test_parse_cron(self):
        scheduler = Scheduler()
        cron_schedule = "*/5 * * * *"
        result = scheduler.parse_cron(cron_schedule)
        expected = {
            "minute": "*/5",
            "hour": "*",
            "day": "*",
            "month": "*",
            "day_of_week": "*",
        }
        self.assertEqual(result, expected)

    @patch(".scheduler.BackgroundScheduler")
    def test_start_scheduler(self, MockBackgroundScheduler):
        mock_scheduler = MockBackgroundScheduler.return_value
        scheduler = Scheduler()
        scheduler.scheduler = mock_scheduler
        scheduler.schedule = "*/5 * * * *"
        scheduler.start()
        self.assertTrue(mock_scheduler.add_job.called)
        self.assertTrue(mock_scheduler.start.called)

    @patch(".scheduler.BackgroundScheduler")
    def test_stop_scheduler(self, MockBackgroundScheduler):
        mock_scheduler = MockBackgroundScheduler.return_value
        scheduler = Scheduler()
        scheduler.scheduler = mock_scheduler
        scheduler.stop()
        mock_scheduler.shutdown.assert_called_once()