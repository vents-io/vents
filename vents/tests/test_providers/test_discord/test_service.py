import os

from unittest import TestCase
from unittest.mock import MagicMock, patch

from vents.providers.discord.service import DiscordService, DiscordWebhookService


class TestDiscordService(TestCase):
    def setUp(self):
        self.token = "test-discord-token"
        self.intents = {"message_content": True, "guilds": True}

    def test_init(self):
        service = DiscordService(token=self.token, intents=self.intents)
        self.assertEqual(service.token, self.token)
        self.assertEqual(service.intents, self.intents)
        self.assertFalse(service.is_async)

    @patch("vents.providers.discord.service.get_token")
    @patch("vents.providers.discord.service.get_discord_intents")
    def test_load_from_connection_with_secret(self, mock_get_intents, mock_get_token):
        mock_get_token.return_value = self.token
        mock_get_intents.return_value = self.intents

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"

        service = DiscordService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.token, self.token)
        self.assertEqual(service.intents, self.intents)
        mock_get_token.assert_called_once_with(context_paths=["/path/to/secret"])
        mock_get_intents.assert_called_once_with(context_paths=["/path/to/secret"])

    @patch("vents.providers.discord.service.get_token")
    @patch("vents.providers.discord.service.get_discord_intents")
    def test_load_from_connection_without_connection(
        self, mock_get_intents, mock_get_token
    ):
        mock_get_token.return_value = self.token
        mock_get_intents.return_value = self.intents

        service = DiscordService.load_from_connection(connection=None)

        self.assertEqual(service.token, self.token)
        self.assertEqual(service.intents, self.intents)
        mock_get_token.assert_called_once_with(context_paths=[])
        mock_get_intents.assert_called_once_with(context_paths=[])

    @patch("discord.Client")
    def test_set_session(self, mock_client):
        service = DiscordService(token=self.token, intents=self.intents)
        service._set_session()

        mock_client.assert_called_once()
        # Verify the client was initialized with correct parameters
        call_kwargs = mock_client.call_args[1]
        self.assertEqual(call_kwargs["token"], self.token)
        self.assertTrue(hasattr(call_kwargs["intents"], "message_content"))

    def test_set_env_vars(self):
        service = DiscordService(token=self.token)
        service.set_env_vars()
        self.assertEqual(os.environ.get("DISCORD_TOKEN"), self.token)


class TestDiscordWebhookService(TestCase):
    def setUp(self):
        self.webhook_url = "https://discord.com/api/webhooks/test"

    def test_init(self):
        service = DiscordWebhookService(url=self.webhook_url)
        self.assertEqual(service.url, self.webhook_url)

    @patch("vents.providers.discord.service.get_webhook_url")
    def test_load_from_connection_with_secret(self, mock_get_webhook_url):
        mock_get_webhook_url.return_value = self.webhook_url

        mock_connection = MagicMock()
        mock_connection.secret.url = "/path/to/webhook"

        service = DiscordWebhookService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.url, self.webhook_url)
        mock_get_webhook_url.assert_called_once_with(context_paths=["/path/to/webhook"])

    @patch("vents.providers.discord.service.get_webhook_url")
    def test_load_from_connection_without_connection(self, mock_get_webhook_url):
        mock_get_webhook_url.return_value = self.webhook_url

        service = DiscordWebhookService.load_from_connection(connection=None)

        self.assertEqual(service.url, self.webhook_url)
        mock_get_webhook_url.assert_called_once_with(context_paths=[])
