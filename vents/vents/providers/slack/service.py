import os

from typing import TYPE_CHECKING, Optional

from vents.providers.base import BaseHttpService, BaseService
from vents.settings import VENTS_CONFIG

if TYPE_CHECKING:
    from vents.connections.connection import Connection


class SlackService(BaseService):
    token: Optional[str] = None
    is_async: bool = False

    @classmethod
    def load_from_connection(
        cls,
        connection: Optional["Connection"],
    ) -> Optional["SlackService"]:
        # Check if there are mounting based on secrets/configmaps
        context_paths = []
        schema = None
        builtin_env = None
        if connection:
            if connection.secret and connection.secret.mount_path:
                context_paths.append(connection.secret.mount_path)
            if connection.config_map and connection.config_map.mount_path:
                context_paths.append(connection.config_map.mount_path)
            if connection.schema_:
                schema = connection.get_schema_as_dict()
            if connection.env:
                builtin_env = connection.env

        token = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["SLACK_TOKEN"],
        )
        return cls(token=token)

    def _set_session(self):
        from slack import AsyncWebClient, WebClient

        self._session = (
            AsyncWebClient(token=self.token)
            if self.is_async
            else WebClient(token=self.token)
        )

    def set_env_vars(self):
        if self.token:
            os.environ["SLACK_TOKEN"] = self.token


class SlackWebhookService(BaseService):
    url: Optional[str] = None
    is_async: bool = False

    @classmethod
    def load_from_connection(
        cls,
        connection: Optional["Connection"],
    ) -> Optional["SlackWebhookService"]:
        # Check if there are mounting based on secrets/configmaps
        context_paths = []
        if connection:
            if connection.secret and connection.secret.url:
                context_paths.append(connection.secret.url)
        url = VENTS_CONFIG.read_keys(context_paths=context_paths, keys=["SLACK_URL"])
        return cls(url=url)

    def _set_session(self):
        from slack import AsyncWebhookClient, WebhookClient

        self._session = (
            AsyncWebhookClient(url=self.url)
            if self.is_async
            else WebhookClient(url=self.url)
        )

    def set_env_vars(self):
        if self.url:
            os.environ["SLACK_URL"] = self.url


class SlackHttpWebhookService(BaseHttpService):
    @classmethod
    def load_from_connection(
        cls, connection: Optional["Connection"]
    ) -> Optional["SlackHttpWebhookService"]:
        # Check if there are mounting based on secrets/configmaps
        context_paths = []
        if connection:
            if connection.secret and connection.secret.url:
                context_paths.append(connection.secret.url)
        url = VENTS_CONFIG.read_keys(context_paths=context_paths, keys=["SLACK_URL"])
        method = VENTS_CONFIG.read_keys(
            context_paths=context_paths, keys=["SLACK_METHOD"]
        )
        session_attrs = VENTS_CONFIG.read_keys(
            context_paths=context_paths, keys=["SLACK_SESSION_ATTRS"]
        )
        return cls(url=url, method=method, session_attrs=session_attrs)
