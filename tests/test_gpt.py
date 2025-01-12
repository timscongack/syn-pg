import unittest
from unittest.mock import patch, MagicMock
from src.gpt import GPTQueryGenerator


class TestGPTQueryGenerator(unittest.TestCase):
    @patch("src.gpt.openai.ChatCompletion.create")
    def test_generate_queries_good_response(self, mock_openai):
        mock_openai.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "['INSERT INTO test_table (id, name) VALUES (1, \"Test\");', "
                                   "'UPDATE test_table SET name = \"Updated\" WHERE id = 1;', "
                                   "'DELETE FROM test_table WHERE id = 1;']"
                    }
                }
            ]
        }

        gpt_generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE test_table (id INT PRIMARY KEY, name TEXT);"]
        queries = gpt_generator.generate_queries(ddl, num_queries=3)

        self.assertEqual(len(queries), 3)
        self.assertIn("INSERT INTO test_table (id, name) VALUES (1, \"Test\");", queries)
        self.assertIn("UPDATE test_table SET name = \"Updated\" WHERE id = 1;", queries)
        self.assertIn("DELETE FROM test_table WHERE id = 1;", queries)

    @patch("src.gpt.openai.ChatCompletion.create")
    def test_generate_queries_malformed_response(self, mock_openai):
        mock_openai.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "{'INSERT INTO test_table (id, name) VALUES (1, \"Test\");'}"
                    }
                }
            ]
        }

        gpt_generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE test_table (id INT PRIMARY KEY, name TEXT);"]
        queries = gpt_generator.generate_queries(ddl, num_queries=3)

        self.assertEqual(len(queries), 0)

    @patch("src.gpt.openai.ChatCompletion.create")
    def test_generate_queries_error_handling(self, mock_openai):
        mock_openai.side_effect = Exception("OpenAI API Error")

        gpt_generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE test_table (id INT PRIMARY KEY, name TEXT);"]
        queries = gpt_generator.generate_queries(ddl, num_queries=3)

        self.assertEqual(len(queries), 0)

    def test_construct_prompt(self):
        gpt_generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE test_table (id INT PRIMARY KEY, name TEXT);"]
        prompt = gpt_generator.construct_prompt(ddl, num_queries=3, percent_inserts=50, percent_updates=30, percent_deletes=20)

        self.assertIn("CREATE TABLE test_table (id INT PRIMARY KEY, name TEXT);", prompt)
        self.assertIn("generate 3 SQL queries", prompt)
        self.assertIn("50% INSERTs, 30% UPDATEs, and 20% DELETEs", prompt)


if __name__ == "__main__":
    unittest.main()