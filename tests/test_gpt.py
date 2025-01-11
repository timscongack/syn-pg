import unittest
from unittest.mock import patch, MagicMock
from src.gpt import GPTQueryGenerator


class TestGPTQueryGenerator(unittest.TestCase):
    @patch("src.gpt.openai")
    def test_generate_queries_good_response(self, mock_openai):
        """Test generating queries with a well-formed response."""
        mock_openai.Completion.create.return_value = {
            "choices": [{"text": "['INSERT INTO test (id) VALUES (1);']"}]
        }

        generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]
        queries = generator.generate_queries(ddl)

        self.assertIn("INSERT INTO test (id) VALUES (1);", queries)
        mock_openai.Completion.create.assert_called_once()

    @patch("src.gpt.openai")
    def test_generate_queries_malformed_response(self, mock_openai):
        """Test generating queries with a malformed response."""
        mock_openai.Completion.create.return_value = {
            "choices": [{"text": "INVALID_RESPONSE"}]
        }

        generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]

        with self.assertRaises(ValueError) as context:
            generator.generate_queries(ddl)
        self.assertIn("Malformed response", str(context.exception))

    @patch("src.gpt.openai")
    def test_generate_queries_caller(self, mock_openai):
        """Test that the caller sends the correct data to OpenAI."""
        generator = GPTQueryGenerator()
        ddl = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]

        mock_openai.Completion.create.return_value = {
            "choices": [{"text": "['INSERT INTO test (id) VALUES (1);']"}]
        }

        generator.generate_queries(ddl)
        mock_openai.Completion.create.assert_called_once_with(
            model="text-davinci-003",
            prompt=generator.construct_prompt(ddl),
            max_tokens=1500,
            temperature=0.7,
            n=1
        )


if __name__ == "__main__":
    unittest.main()