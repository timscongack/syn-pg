import logging
from .db import Database
from .gpt import GPTQueryGenerator
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data_generator.log"),
        logging.StreamHandler(),
    ]
)

class DataGenerator:
    def __init__(self, db: Database):
        """Initialize the DataGenerator with a database connection and GPT query generator."""
        self.db = db
        self.gpt = GPTQueryGenerator()

    def generate_and_run_queries(self) -> None:
        """
        Generate synthetic SQL queries and execute them on the database.

        If a query fails, it skips to the next one.
        """
        try:
            self.db.connect()
            logging.info("Connected to the database.")
            ddl = self.db.get_all_ddl()
            logging.info(f"Retrieved DDL: {ddl}")
            queries = self.gpt.generate_queries(ddl)
            logging.info(f"Generated {len(queries)} queries.")
            for query in queries:
                try:
                    with self.db.connection.cursor() as cur:
                        cur.execute("BEGIN;")
                        cur.execute(query)
                        cur.execute("COMMIT;")
                        logging.info(f"Executed query successfully: {query}")
                except Exception as e:
                    logging.error(f"Failed to execute query: {query}\nError: {e}")
                    self.db.connection.rollback()
                    logging.info("Transaction rolled back.")
        except Exception as e:
            logging.critical(f"An unexpected error occurred: {e}")
        finally:
            self.db.close()
            logging.info("Closed database connection.")