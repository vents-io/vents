import os

from unittest import TestCase
from unittest.mock import MagicMock, patch

from vents.config import AppConfig
from vents.providers.openai.service import OpenAIService


class TestOpenAIService(TestCase):
    def setUp(self):
        self.api_key = "test-openai-key"
        self.base_url = "https://api.openai.com/v1"
        self.kwargs = {"timeout": 30}

    def test_init(self):
        service = OpenAIService(
            api_key=self.api_key, base_url=self.base_url, kwargs=self.kwargs
        )
        self.assertEqual(service.api_key, self.api_key)
        self.assertEqual(service.base_url, self.base_url)
        self.assertEqual(service.kwargs, self.kwargs)
        self.assertFalse(service.is_async)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret_and_config(self, mock_read_keys):
        mock_read_keys.side_effect = [self.api_key, self.base_url, self.kwargs]

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"
        mock_connection.config_map.mount_path = "/path/to/config"
        mock_connection.schema = None
        mock_connection.env = None

        service = OpenAIService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.api_key, self.api_key)
        self.assertEqual(service.base_url, self.base_url)
        self.assertEqual(service.kwargs, self.kwargs)

        expected_paths = ["/path/to/secret", "/path/to/config"]
        mock_read_keys.assert_any_call(
            context_paths=expected_paths, keys=["OPENAI_API_KEY"], schema=None, env=None
        )
        mock_read_keys.assert_any_call(
            context_paths=expected_paths,
            keys=["OPENAI_BASE_URL"],
            schema=None,
            env=None,
        )
        mock_read_keys.assert_any_call(
            context_paths=expected_paths, keys=["OPENAI_KWARGS"], schema=None, env=None
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret_only(self, mock_read_keys):
        mock_read_keys.side_effect = [self.api_key, None, None]

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"

        service = OpenAIService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.api_key, self.api_key)
        self.assertEqual(service.base_url, None)
        self.assertEqual(service.kwargs, None)
