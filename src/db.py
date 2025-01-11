import os
import logging
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class Database:
    def __init__(self) -> None:
        """Initialize the Database object with connection details from environment variables."""
        self.connection: Optional[connection] = None
        self.host: str = os.getenv("POSTGRES_HOST")
        self.port: int = int(os.getenv("POSTGRES_PORT"))
        self.user: str = os.getenv("POSTGRES_USER")
        self.password: str = os.getenv("POSTGRES_PASSWORD")
        self.database: str = os.getenv("POSTGRES_DB")

        if not all([self.host, self.port, self.user, self.password, self.database]):
            raise EnvironmentError("Missing required database configuration in .env file.")

    def connect(self) -> None:
        """Establish a connection to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            logging.info("Database connection established.")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to the database: {e}")

    def get_table_columns(self, table_name: str) -> List[tuple]:
        """Retrieve the column definitions for a specific table."""
        if not self.connection:
            raise ConnectionError("Database connection is not established.")

        query = (
            "SELECT column_name, data_type "
            "FROM information_schema.columns "
            "WHERE table_name = %s AND table_schema = 'public';"
        )
        with self.connection.cursor() as cur:
            cur.execute(query, (table_name,))
            return cur.fetchall()

    def get_all_table_columns(self) -> Dict[str, List[Dict[str, str]]]:
        """Retrieve the column definitions for all tables in the public schema."""
        if not self.connection:
            raise ConnectionError("Database connection is not established.")

        query = (
            "SELECT table_name, column_name, data_type "
            "FROM information_schema.columns "
            "WHERE table_schema = 'public';"
        )
        with self.connection.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            table_columns = {}
            for table_name, column_name, data_type in results:
                if table_name not in table_columns:
                    table_columns[table_name] = []
                table_columns[table_name].append({"column_name": column_name, "data_type": data_type})
            return table_columns

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")
        else:
            logging.info("No active database connection to close.")