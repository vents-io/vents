import os

from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from vents.config import AppConfig
from vents.providers.slack.service import (
    SlackHttpWebhookService,
    SlackService,
    SlackWebhookService,
)


class TestSlackService(TestCase):
    def setUp(self):
        self.token = "test-slack-token"

    def test_init(self):
        service = SlackService(token=self.token)
        self.assertEqual(service.token, self.token)
        self.assertFalse(service.is_async)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret(self, mock_read_keys):
        mock_read_keys.return_value = self.token

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"
        mock_connection.schema_ = None
        mock_connection.env = None
        mock_connection.config_map = None

        service = SlackService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.token, self.token)
        mock_read_keys.assert_called_once_with(
            context_paths=["/path/to/secret"],
            schema=None,
            env=None,
            keys=["SLACK_TOKEN"],
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_without_connection(self, mock_read_keys):
        mock_read_keys.return_value = self.token

        service = SlackService.load_from_connection(connection=None)

        self.assertEqual(service.token, self.token)
        mock_read_keys.assert_called_once_with(
            context_paths=[], schema=None, env=None, keys=["SLACK_TOKEN"]
        )

    @patch("slack.WebClient")
    def test_set_session_sync(self, mock_web_client):
        service = SlackService(token=self.token)
        service._set_session()

        mock_web_client.assert_called_once_with(token=self.token)

    @patch("slack.AsyncWebClient")
    def test_set_session_async(self, mock_async_web_client):
        service = SlackService(token=self.token, is_async=True)
        service._set_session()

        mock_async_web_client.assert_called_once_with(token=self.token)

    def test_set_env_vars(self):
        service = SlackService(token=self.token)
        service.set_env_vars()
        self.assertEqual(os.environ.get("SLACK_TOKEN"), self.token)


class TestSlackWebhookService(TestCase):
    def setUp(self):
        self.url = "https://hooks.slack.com/services/test"

    def test_init(self):
        service = SlackWebhookService(url=self.url)
        self.assertEqual(service.url, self.url)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret(self, mock_read_keys):
        mock_read_keys.return_value = self.url

        mock_connection = MagicMock()
        mock_connection.secret.url = "/path/to/webhook"

        service = SlackWebhookService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.url, self.url)
        mock_read_keys.assert_called_once_with(
            context_paths=["/path/to/webhook"], keys=["SLACK_URL"]
        )

    @patch("slack.WebhookClient")
    def test_set_session_sync(self, mock_webhook_client):
        service = SlackWebhookService(url=self.url)
        service._set_session()

        mock_webhook_client.assert_called_once_with(url=self.url)

    @patch("slack.AsyncWebhookClient")
    def test_set_session_async(self, mock_async_webhook_client):
        service = SlackWebhookService(url=self.url, is_async=True)
        service._set_session()

        mock_async_webhook_client.assert_called_once_with(url=self.url)

    def test_set_env_vars(self):
        service = SlackWebhookService(url=self.url)
        service.set_env_vars()
        self.assertEqual(os.environ.get("SLACK_URL"), self.url)


class TestSlackHttpWebhookService(TestCase):
    def setUp(self):
        self.url = "https://hooks.slack.com/services/test"
        self.method = "POST"
        self.session_attrs = {"timeout": 10}

    def test_init(self):
        service = SlackHttpWebhookService(
            url=self.url, method=self.method, session_attrs=self.session_attrs
        )
        self.assertEqual(service.url, self.url)
        self.assertEqual(service.method, self.method)
        self.assertEqual(service.session_attrs, self.session_attrs)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret(self, mock_read_keys):
        mock_read_keys.side_effect = [self.url, self.method, self.session_attrs]

        mock_connection = MagicMock()
        mock_connection.secret.url = "/path/to/webhook"

        service = SlackHttpWebhookService.load_from_connection(
            connection=mock_connection
        )

        self.assertEqual(service.url, self.url)
        self.assertEqual(service.method, self.method)
        self.assertEqual(service.session_attrs, self.session_attrs)

        mock_read_keys.assert_has_calls(
            [
                call(context_paths=["/path/to/webhook"], keys=["SLACK_URL"]),
                call(context_paths=["/path/to/webhook"], keys=["SLACK_METHOD"]),
                call(context_paths=["/path/to/webhook"], keys=["SLACK_SESSION_ATTRS"]),
            ]
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_without_connection(self, mock_read_keys):
        mock_read_keys.side_effect = [self.url, self.method, self.session_attrs]

        service = SlackHttpWebhookService.load_from_connection(connection=None)

        self.assertEqual(service.url, self.url)
        self.assertEqual(service.method, self.method)
        self.assertEqual(service.session_attrs, self.session_attrs)

        mock_read_keys.assert_has_calls(
            [
                call(context_paths=[], keys=["SLACK_URL"]),
                call(context_paths=[], keys=["SLACK_METHOD"]),
                call(context_paths=[], keys=["SLACK_SESSION_ATTRS"]),
            ]
        )
