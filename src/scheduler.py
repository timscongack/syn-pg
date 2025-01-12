import os
from typing import Callable
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from .db import Database
from .gpt import GPTQueryGenerator
from .data_generator import DataGenerator
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Scheduler:
    def __init__(self):
        self.schedule = os.getenv("SCHEDULE_CRON")
        if not self.schedule:
            raise EnvironmentError("Missing SCHEDULE_CRON in .env file.")
        self.db = Database()
        self.data_generator = DataGenerator(self.db)
        self.scheduler = BackgroundScheduler()

    def execute_process(self) -> None:
        """
        Executes the data generation and query process using DataGenerator.
        """
        logging.info("Scheduler started executing the process.")
        try:
            self.data_generator.generate_and_run_queries()
        except Exception as e:
            logging.error(f"An error occurred during execution: {e}")
        finally:
            logging.info("Process execution completed.")

    def start(self) -> None:
        """
        Starts the scheduler with the CRON schedule provided in the environment.
        """
        cron_params = self.parse_cron(self.schedule)
        self.scheduler.add_job(self.execute_process, "cron", **cron_params)
        self.scheduler.start()
        logging.info("Scheduler started with CRON schedule: %s", self.schedule)

    def parse_cron(self, cron_string: str) -> dict:
        """
        Parses the CRON string from the environment into a dictionary for APScheduler.
        """
        cron_parts = cron_string.split()
        if len(cron_parts) != 5:
            raise ValueError("Invalid CRON schedule format in SCHEDULE_CRON.")
        return {
            "minute": cron_parts[0],
            "hour": cron_parts[1],
            "day": cron_parts[2],
            "month": cron_parts[3],
            "day_of_week": cron_parts[4],
        }

    def stop(self) -> None:
        """
        Stops the scheduler gracefully.
        """
        self.scheduler.shutdown()
        logging.info("Scheduler stopped successfully.")