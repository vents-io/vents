import os

from typing import TYPE_CHECKING, Dict, Optional

from vents.providers.base import BaseHttpService, BaseService
from vents.settings import VENTS_CONFIG

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
        schema = None
        builtin_env = None
        if connection:
            if connection.secret and connection.secret.mount_path:
                context_paths.append(connection.secret.mount_path)
            if connection.schema:
                schema = connection.schema
            if connection.env:
                builtin_env = connection.env

        token = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["DISCORD_TOKEN"],
        )
        intents = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["DISCORD_INTENTS"],
        )
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
        url = VENTS_CONFIG.read_keys(context_paths=context_paths, keys=["DISCORD_URL"])
        return cls(url=url)
