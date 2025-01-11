import os
import psycopg2

def test_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        conn.close()
        print("Database connection successful.")
    except psycopg2.Error as e:
        raise ConnectionError(f"Failed to connect to the database: {e}")