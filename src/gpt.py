import openai
from typing import List
import os
from dotenv import load_dotenv
import ast
import logging

num_tokens = 4000
load_dotenv()

class GPTQueryGenerator:
    def __init__(self):
        self.api_key: str = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing OpenAI API key in .env file.")
        openai.api_key = self.api_key

    def construct_prompt(self, ddl: List[str], num_queries: int = 10, percent_inserts: int = 50, percent_updates: int = 30, percent_deletes: int = 20) -> str:
        prompt = (
            "You are a SQL query generator. Based on the provided database schema definitions (DDL), "
            f"generate {num_queries} SQL queries that mimic realistic database operations. "
            f"The queries should consist of {percent_inserts}% INSERTs, {percent_updates}% UPDATEs, and {percent_deletes}% DELETEs. "
            "The queries must:\n"
            "- Adhere to constraints in the schema (e.g., foreign keys, primary keys, unique constraints).\n"
            "- Be idempotent when executed.\n"
            "- Include valid values for data types (e.g., strings, numbers, dates).\n"
            "- Use subqueries to select random records for UPDATEs and DELETEs, e.g., "
            "SELECT id FROM table_name ORDER BY RANDOM() LIMIT 1;\n"
            "- Be returned as a Python list of SQL strings, formatted correctly for Python syntax.\n"
            "- Make the data realistic, also creative but appropriate.\n"
            f"- Limit the response to {num_tokens} tokens.\n\n"
            "Here is the database schema:\n"
        )
        for table_ddl in ddl:
            prompt += f"{table_ddl}\n\n"
        prompt += "Generate the SQL queries now:"
        return prompt

    def generate_queries(self, ddl: List[str], num_queries: int = 10, percent_inserts: int = 50, percent_updates: int = 30, percent_deletes: int = 20) -> List[str]:
        prompt = self.construct_prompt(ddl, num_queries, percent_inserts, percent_updates, percent_deletes)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=num_tokens,
                temperature=0.7,
                n=1
            )
            raw_response = response["choices"][0]["message"]["content"].strip()
            logging.info(f"Raw GPT response: {raw_response}")

            if raw_response.startswith("```"):
                raw_response = raw_response.strip("```").strip()
                if "sql_queries = " in raw_response:
                    raw_response = raw_response.split("sql_queries = ", 1)[-1].strip()

            queries = ast.literal_eval(raw_response)
            if not isinstance(queries, list) or not all(isinstance(query, str) for query in queries):
                raise ValueError("Response is not a valid list of SQL strings.")
            return queries

        except (SyntaxError, ValueError) as e:
            logging.error(f"Malformed response from OpenAI: {e}")
            return []
        except Exception as e:
            logging.error(f"Error generating queries: {e}")
            return []