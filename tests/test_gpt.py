import unittest
from unittest.mock import MagicMock, patch
from src.gpt import GPTQueryGenerator


class TestGPTQueryGenerator(unittest.TestCase):
    @patch("src.gpt.openai")
    def test_generate_queries_good_response(self, mock_openai):
        """Test generating queries with a well-formed response."""
        mock_openai.ChatCompletion.create.return_value = {
            "choices": [{"message": {"content": "['INSERT INTO test (id) VALUES (1);']"}}]
        }

        generator = GPTQueryGenerator()

        ddl = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]

        queries = generator.generate_queries(ddl)

        print(f"Generated queries: {queries}")
        self.assertIn("INSERT INTO test (id) VALUES (1);", queries)

        mock_openai.ChatCompletion.create.assert_called_once()

    @patch("src.gpt.openai")
    def test_generate_queries_malformed_response(self, mock_openai):
        """Test generating queries with a malformed response."""
        mock_openai.ChatCompletion.create.return_value = {
            "choices": [{"message": {"content": "INVALID_RESPONSE"}}]
        }

        generator = GPTQueryGenerator()

        ddl = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]

        with self.assertRaises(ValueError) as context:
            generator.generate_queries(ddl)

        self.assertIn("Malformed response", str(context.exception))
        mock_openai.ChatCompletion.create.assert_called_once()

    @patch("src.gpt.openai")
    def test_generate_queries_caller(self, mock_openai):
        """Test that the caller sends the correct data to OpenAI."""
        generator = GPTQueryGenerator()

        ddl = ["CREATE TABLE test (id SERIAL PRIMARY KEY);"]

        generator.generate_queries(ddl)

        mock_openai.ChatCompletion.create.assert_called_once()
        call_args = mock_openai.ChatCompletion.create.call_args[1]

        self.assertIn("messages", call_args)
        self.assertEqual(call_args["messages"][0]["content"], ddl[0])


if __name__ == "__main__":
    unittest.main()