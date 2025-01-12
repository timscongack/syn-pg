import unittest
from unittest.mock import patch, MagicMock
from src.scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    @patch("src.scheduler.BackgroundScheduler")
    @patch("src.scheduler.Database")
    @patch("src.scheduler.DataGenerator")
    def test_execute_process(
        self,
        MockDataGenerator: MagicMock,
        MockDatabase: MagicMock,
        MockBackgroundScheduler: MagicMock,
    ):
        mock_db = MockDatabase.return_value
        mock_data_generator = MockDataGenerator.return_value

        scheduler = Scheduler()
        scheduler.db = mock_db
        scheduler.data_generator = mock_data_generator

        scheduler.execute_process()

        mock_data_generator.generate_and_run_queries.assert_called_once()

    def test_parse_cron(self):
        scheduler = Scheduler()
        cron_params = scheduler.parse_cron("* * * * *")
        self.assertEqual(cron_params, {
            "minute": "*",
            "hour": "*",
            "day": "*",
            "month": "*",
            "day_of_week": "*",
        })

    @patch("src.scheduler.BackgroundScheduler")
    @patch("os.getenv")
    def test_start_scheduler(self, mock_getenv: MagicMock, MockBackgroundScheduler: MagicMock):
        mock_scheduler_instance = MockBackgroundScheduler.return_value

        def mock_getenv_side_effect(key):
            if key == "SCHEDULE_CRON":
                return "* * * * *"
            elif key == "POSTGRES_PORT":
                return "5432"
            elif key == "OPENAI_API_KEY":
                return "dummy_api_key"
            elif key.startswith("POSTGRES"):
                return "dummy_value"
            return None

        mock_getenv.side_effect = mock_getenv_side_effect

        scheduler = Scheduler()
        scheduler.start()
        mock_scheduler_instance.add_job.assert_called_once_with(
            scheduler.execute_process, "cron",
            minute="*",
            hour="*",
            day="*",
            month="*",
            day_of_week="*"
        )
        mock_scheduler_instance.start.assert_called_once()

    @patch("src.scheduler.BackgroundScheduler")
    def test_stop_scheduler(self, MockBackgroundScheduler: MagicMock):
        mock_scheduler_instance = MockBackgroundScheduler.return_value
        scheduler = Scheduler()
        scheduler.scheduler = mock_scheduler_instance
        scheduler.stop()
        mock_scheduler_instance.shutdown.assert_called_once()


if __name__ == "__main__":
    unittest.main()