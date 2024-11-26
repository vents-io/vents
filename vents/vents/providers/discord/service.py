import os

from typing import TYPE_CHECKING, Dict, Optional

from vents.providers.base import BaseHttpService, BaseService
from vents.providers.discord.base import get_discord_intents, get_token, get_webhook_url

if TYPE_CHECKING:
    from vents.connections.connection import Connection


class DiscordService(BaseService):
    token: Optional[str] = None
    is_async: bool = False
    intents: Optional[Dict] = None

    @classmethod
    def load_from_connection(
        cls,
        connection: Optional["Connection"],
    ) -> Optional["DiscordService"]:
        # Check if there are mounting based on secrets/configmaps
        context_paths = []
        if connection:
            if connection.secret and connection.secret.mount_path:
                context_paths.append(connection.secret.mount_path)
        token = get_token(context_paths=context_paths)
        intents = get_discord_intents(context_paths=context_paths)
        return cls(token=token, intents=intents)

    def _set_session(self):
        import discord

        intents = discord.Intents.default()
        _intents = self.intents or {}
        for intent, value in _intents.items():
            setattr(intents, intent, value)
        self._session = discord.Client(intents=intents, token=self.token)

    def set_env_vars(self):
        if self.token:
            os.environ["DISCORD_TOKEN"] = self.token


class DiscordWebhookService(BaseHttpService):
    url: Optional[str] = None

    @classmethod
    def load_from_connection(
        cls,
        connection: Optional["Connection"],
    ) -> Optional["DiscordWebhookService"]:
        context_paths = []
        if connection:
            if connection.secret and connection.secret.url:
                context_paths.append(connection.secret.url)
        url = get_webhook_url(context_paths=context_paths)
        return cls(url=url)
