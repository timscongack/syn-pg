import os
import logging
from typing import List, Optional
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class Database:
    def __init__(self) -> None:
        self.connection: Optional[connection] = None
        self.host: str = os.getenv("POSTGRES_HOST")
        self.port: int = int(os.getenv("POSTGRES_PORT"))
        self.user: str = os.getenv("POSTGRES_USER")
        self.password: str = os.getenv("POSTGRES_PASSWORD")
        self.database: str = os.getenv("POSTGRES_DB")
        if not all([self.host, self.port, self.user, self.password, self.database]):
            raise EnvironmentError("Missing required database configuration in .env file.")

    def connect(self) -> None:
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

    def get_all_ddl(self) -> List[str]:
        """
        Retrieve DDL statements for all tables and views in the public schema.

        Returns:
            List[str]: List of DDL statements as strings.
        """
        if not self.connection:
            raise ConnectionError("Database connection is not established.")

        table_query = """
            SELECT 'CREATE TABLE ' || table_name || E' (\n' ||
                array_to_string(
                    array_agg(column_name || ' ' || data_type), E',\n'
                ) || E'\n);' AS table_ddl
            FROM information_schema.columns
            WHERE table_schema = 'public'
            GROUP BY table_name;
        """

        view_query = """
            SELECT 'CREATE VIEW ' || table_name || E' AS\n' || view_definition AS view_ddl
            FROM information_schema.views
            WHERE table_schema = 'public';
        """

        ddl_statements = []
        with self.connection.cursor() as cur:
            cur.execute(table_query)
            table_ddl = [row[0] for row in cur.fetchall()]
            ddl_statements.extend(table_ddl)

            cur.execute(view_query)
            view_ddl = [row[0] for row in cur.fetchall()]
            ddl_statements.extend(view_ddl)

        return ddl_statements

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")
        else:
            logging.info("No active database connection to close.")