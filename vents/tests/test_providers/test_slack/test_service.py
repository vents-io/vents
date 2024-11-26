import os

from unittest import TestCase
from unittest.mock import MagicMock, patch

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

    @patch("vents.providers.slack.service.get_token")
    def test_load_from_connection_with_secret(self, mock_get_token):
        mock_get_token.return_value = self.token

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"

        service = SlackService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.token, self.token)
        mock_get_token.assert_called_once_with(context_paths=["/path/to/secret"])

    @patch("vents.providers.slack.service.get_token")
    def test_load_from_connection_without_connection(self, mock_get_token):
        mock_get_token.return_value = self.token

        service = SlackService.load_from_connection(connection=None)

        self.assertEqual(service.token, self.token)
        mock_get_token.assert_called_once_with(context_paths=[])

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

    @patch("vents.providers.slack.service.get_url")
    def test_load_from_connection_with_secret(self, mock_get_url):
        mock_get_url.return_value = self.url

        mock_connection = MagicMock()
        mock_connection.secret.url = "/path/to/webhook"

        service = SlackWebhookService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.url, self.url)
        mock_get_url.assert_called_once_with(context_paths=["/path/to/webhook"])

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

    @patch("vents.providers.slack.service.get_url")
    @patch("vents.providers.slack.service.get_method")
    @patch("vents.providers.slack.service.get_session_attrs")
    def test_load_from_connection_with_secret(
        self, mock_get_session_attrs, mock_get_method, mock_get_url
    ):
        mock_get_url.return_value = self.url
        mock_get_method.return_value = self.method
        mock_get_session_attrs.return_value = self.session_attrs

        mock_connection = MagicMock()
        mock_connection.secret.url = "/path/to/webhook"

        service = SlackHttpWebhookService.load_from_connection(
            connection=mock_connection
        )

        self.assertEqual(service.url, self.url)
        self.assertEqual(service.method, self.method)
        self.assertEqual(service.session_attrs, self.session_attrs)

        mock_get_url.assert_called_once_with(context_paths=["/path/to/webhook"])
        mock_get_method.assert_called_once_with(context_paths=["/path/to/webhook"])
        mock_get_session_attrs.assert_called_once_with(
            context_paths=["/path/to/webhook"]
        )

    @patch("vents.providers.slack.service.get_url")
    @patch("vents.providers.slack.service.get_method")
    @patch("vents.providers.slack.service.get_session_attrs")
    def test_load_from_connection_without_connection(
        self, mock_get_session_attrs, mock_get_method, mock_get_url
    ):
        mock_get_url.return_value = self.url
        mock_get_method.return_value = self.method
        mock_get_session_attrs.return_value = self.session_attrs

        service = SlackHttpWebhookService.load_from_connection(connection=None)

        self.assertEqual(service.url, self.url)
        self.assertEqual(service.method, self.method)
        self.assertEqual(service.session_attrs, self.session_attrs)

        mock_get_url.assert_called_once_with(context_paths=[])
        mock_get_method.assert_called_once_with(context_paths=[])
        mock_get_session_attrs.assert_called_once_with(context_paths=[])
