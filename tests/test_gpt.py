import unittest
from unittest.mock import patch
from .gpt import GPTQueryGenerator

class TestGPTQueryGenerator(unittest.TestCase):
    @patch("openai.Completion.create")
    def test_generate_queries(self, mock_openai_create):
        mock_response = {
            "choices": [
                {
                    "text": "['INSERT INTO users (id, name) VALUES (1, \"Alice\");', 'DELETE FROM users WHERE id = 1;']"
                }
            ]
        }
        mock_openai_create.return_value = mock_response
        gpt_generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));"]
        queries = gpt_generator.generate_queries(ddl)
        mock_openai_create.assert_called_once()
        self.assertEqual(
            queries,
            ['INSERT INTO users (id, name) VALUES (1, "Alice");', 'DELETE FROM users WHERE id = 1;']
        )

    def test_construct_prompt(self):
        gpt_generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));"]
        prompt = gpt_generator.construct_prompt(ddl)
        self.assertIn("CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));", prompt)
        self.assertIn("Generate the SQL queries now:", prompt)