import os

from unittest import TestCase
from unittest.mock import MagicMock, patch

from vents.config import AppConfig
from vents.providers.anthropic.service import AnthropicService


class TestAnthropicService(TestCase):
    def setUp(self):
        self.api_key = "test-anthropic-key"
        self.base_url = "https://api.anthropic.com/v1"
        self.kwargs = {"timeout": 30}

    def test_init(self):
        service = AnthropicService(api_key=self.api_key, kwargs=self.kwargs)
        self.assertEqual(service.api_key, self.api_key)
        self.assertEqual(service.kwargs, self.kwargs)
        self.assertFalse(service.is_async)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret_and_config(self, mock_read_keys):
        mock_read_keys.side_effect = [self.api_key, self.kwargs]

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"
        mock_connection.config_map.mount_path = "/path/to/config"

        service = AnthropicService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.api_key, self.api_key)
        self.assertEqual(service.kwargs, self.kwargs)

        expected_paths = ["/path/to/secret", "/path/to/config"]
        mock_read_keys.assert_any_call(
            context_paths=expected_paths, keys=["ANTHROPIC_API_KEY"]
        )
        mock_read_keys.assert_any_call(
            context_paths=expected_paths, keys=["ANTHROPIC_KWARGS"]
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret_only(self, mock_read_keys):
        mock_read_keys.side_effect = [self.api_key, None]

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"
        mock_connection.config_map = None

        service = AnthropicService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.api_key, self.api_key)
        self.assertIsNone(service.kwargs)

        expected_paths = ["/path/to/secret"]
        mock_read_keys.assert_any_call(
            context_paths=expected_paths, keys=["ANTHROPIC_API_KEY"]
        )
        mock_read_keys.assert_any_call(
            context_paths=expected_paths, keys=["ANTHROPIC_KWARGS"]
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_without_connection(self, mock_read_keys):
        mock_read_keys.side_effect = [self.api_key, None]

        service = AnthropicService.load_from_connection(connection=None)

        self.assertEqual(service.api_key, self.api_key)
        self.assertIsNone(service.kwargs)

        mock_read_keys.assert_any_call(context_paths=[], keys=["ANTHROPIC_API_KEY"])
        mock_read_keys.assert_any_call(context_paths=[], keys=["ANTHROPIC_KWARGS"])

    @patch("anthropic.Anthropic")
    def test_set_session(self, mock_anthropic_client):
        service = AnthropicService(api_key=self.api_key)
        service._set_session()

        mock_anthropic_client.assert_called_once_with(api_key=self.api_key)

    @patch("anthropic.Anthropic")
    def test_set_session_with_kwargs(self, mock_anthropic_client):
        service = AnthropicService(api_key=self.api_key, kwargs=self.kwargs)
        service._set_session()

        mock_anthropic_client.assert_called_once_with(
            api_key=self.api_key, **self.kwargs
        )

    def test_set_env_vars(self):
        service = AnthropicService(api_key=self.api_key, kwargs=self.kwargs)
        service.set_env_vars()

        self.assertEqual(os.environ.get("ANTHROPIC_API_KEY"), self.api_key)
        self.assertEqual(os.environ.get("ANTHROPIC_KWARGS"), '{"timeout":30}')

    def test_set_env_vars_no_values(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("ANTHROPIC_KWARGS", None)
        service = AnthropicService()
        service.set_env_vars()
        self.assertNotIn("ANTHROPIC_API_KEY", os.environ)
        self.assertNotIn("ANTHROPIC_KWARGS", os.environ)
