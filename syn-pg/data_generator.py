from .db import Database
from .gpt import GPTQueryGenerator
from typing import List

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
            ddl = self.db.get_all_ddl()
            queries = self.gpt.generate_queries(ddl)

            for query in queries:
                try:
                    with self.db.connection.cursor() as cur:
                        cur.execute("BEGIN;")
                        cur.execute(query)
                        cur.execute("COMMIT;")
                        print(f"Executed query successfully: {query}")
                except Exception as e:
                    print(f"Failed to execute query: {query}\nError: {e}")
                    self.db.connection.rollback()
        finally:
            self.db.close()