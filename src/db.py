import os
from typing import List, Optional
import psycopg2
from psycopg2.extensions import connection
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

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
            print("Database connection established.")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to the database: {e}")

    def get_table_ddl(self, table_name: str) -> str:
        """
        Retrieve the DDL for a specific table.

        Args:
            table_name (str): Name of the table to retrieve DDL for.

        Returns:
            str: The SQL DDL statement for the table.
        """
        if not self.connection:
            raise ConnectionError("Database connection is not established.")
        
        query = sql.SQL(
            """
            SELECT pg_catalog.pg_get_tabledef(oid)
            FROM pg_catalog.pg_class
            WHERE relname = %s;
            """
        )
        with self.connection.cursor() as cur:
            cur.execute(query, (table_name,))
            result = cur.fetchone()
            if not result:
                raise ValueError(f"No DDL found for table {table_name}")
            return result[0]

    def get_all_ddl(self) -> List[str]:
        """
        Retrieve the DDL for all tables in the current database.

        Returns:
            List[str]: A list of SQL DDL statements for all tables.
        """
        if not self.connection:
            raise ConnectionError("Database connection is not established.")
        
        query = """
            SELECT relname, pg_catalog.pg_get_tabledef(oid)
            FROM pg_catalog.pg_class
            WHERE relkind = 'r' AND relnamespace IN (
                SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = 'public'
            );
        """
        with self.connection.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            return [ddl for _, ddl in results]

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        else:
            print("No active database connection to close.")