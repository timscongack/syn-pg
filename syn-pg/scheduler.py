import os
from typing import Callable
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from .db import Database
from .gpt import GPTQueryGenerator
from .data_generator import DataGenerator

load_dotenv()

class Scheduler:
    def __init__(self):
        self.schedule = os.getenv("SCHEDULE_CRON")
        if not self.schedule:
            raise EnvironmentError("Missing SCHEDULE_CRON in .env file.")
        self.db = Database()
        self.gpt = GPTQueryGenerator()
        self.data_generator = DataGenerator(self.db)
        self.scheduler = BackgroundScheduler()

    def execute_process(self) -> None:
        try:
            self.db.connect()
            ddl = self.db.get_all_ddl()
            queries = self.gpt.generate_queries(ddl)
            for query in queries:
                try:
                    with self.db.connection.cursor() as cur:
                        cur.execute("BEGIN;")
                        cur.execute(query)
                        cur.execute("COMMIT;")
                except Exception as e:
                    self.db.connection.rollback()
        finally:
            self.db.close()

    def start(self) -> None:
        cron_params = self.parse_cron(self.schedule)
        self.scheduler.add_job(self.execute_process, "cron", **cron_params)
        self.scheduler.start()

    def parse_cron(self, cron_string: str) -> dict:
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
        self.scheduler.shutdown()