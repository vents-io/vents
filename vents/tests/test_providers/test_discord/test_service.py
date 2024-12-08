import os

from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from vents.config import AppConfig
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

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret(self, mock_read_keys):
        mock_read_keys.side_effect = [self.token, self.intents]

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"

        service = DiscordService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.token, self.token)
        self.assertEqual(service.intents, self.intents)
        mock_read_keys.assert_has_calls(
            [
                call(
                    context_paths=["/path/to/secret"],
                    schema=mock_connection.get_schema_as_dict(),
                    env=mock_connection.env,
                    keys=["DISCORD_TOKEN"],
                ),
                call(
                    context_paths=["/path/to/secret"],
                    schema=mock_connection.get_schema_as_dict(),
                    env=mock_connection.env,
                    keys=["DISCORD_INTENTS"],
                ),
            ]
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_without_connection(self, mock_read_keys):
        mock_read_keys.side_effect = [self.token, self.intents]

        service = DiscordService.load_from_connection(connection=None)

        self.assertEqual(service.token, self.token)
        self.assertEqual(service.intents, self.intents)
        mock_read_keys.assert_has_calls(
            [
                call(context_paths=[], schema=None, env=None, keys=["DISCORD_TOKEN"]),
                call(context_paths=[], schema=None, env=None, keys=["DISCORD_INTENTS"]),
            ]
        )

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

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret(self, mock_read_keys):
        mock_read_keys.side_effect = [self.webhook_url]

        mock_connection = MagicMock()
        mock_connection.secret.url = "/path/to/webhook"

        service = DiscordWebhookService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.url, self.webhook_url)
        mock_read_keys.assert_called_once_with(
            context_paths=["/path/to/webhook"], keys=["DISCORD_URL"]
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_without_connection(self, mock_read_keys):
        mock_read_keys.side_effect = [self.webhook_url]

        service = DiscordWebhookService.load_from_connection(connection=None)

        self.assertEqual(service.url, self.webhook_url)
        mock_read_keys.assert_called_once_with(context_paths=[], keys=["DISCORD_URL"])
