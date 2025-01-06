import openai
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class GPTQueryGenerator:
    def __init__(self):
        """Initialize GPTQueryGenerator with the OpenAI API key."""
        self.api_key: str = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing OpenAI API key in .env file.")
        openai.api_key = self.api_key

    def construct_prompt(self, ddl: List[str]) -> str:
        """
        Construct a prompt for GPT based on the database DDL.

        Args:
            ddl (List[str]): List of DDL statements describing the database schema.

        Returns:
            str: The constructed prompt for GPT.
        """
        prompt = (
            "You are a SQL expert. Given the following database schema definitions (DDL), "
            "generate synthetic SQL queries to mimic realistic database operations. "
            "The SQL must follow these requirements:\n"
            "1. Obey all constraints defined in the schema (e.g., foreign keys, primary keys, unique constraints).\n"
            "2. Generate INSERT, UPDATE, and DELETE statements.\n"
            "3. Ensure each statement is idempotent within a transaction in PostgreSQL.\n"
            "4. Provide at least one of each type of query (INSERT, UPDATE, DELETE).\n"
            "5. Return the queries as a Python list of SQL strings.\n"
            "Here is the database schema:\n\n"
        )
        for table_ddl in ddl:
            prompt += f"{table_ddl}\n\n"

        prompt += "Generate the SQL queries now:"
        return prompt

    def generate_queries(self, ddl: List[str]) -> List[str]:
        """
        Generate synthetic SQL queries using OpenAI's GPT model.

        Args:
            ddl (List[str]): List of DDL statements describing the database schema.

        Returns:
            List[str]: List of synthetic SQL queries.
        """
        prompt = self.construct_prompt(ddl)
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7,
                n=1
            )
            queries = response['choices'][0]['text'].strip()
            return eval(queries)
        except Exception as e:
            print(f"Error generating queries: {e}")
            return []