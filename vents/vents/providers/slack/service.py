import os

from typing import TYPE_CHECKING, Optional

from vents.providers.base import BaseHttpService, BaseService
from vents.providers.slack.base import get_method, get_session_attrs, get_token, get_url

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
        if connection:
            if connection.secret and connection.secret.mount_path:
                context_paths.append(connection.secret.mount_path)
        token = get_token(context_paths=context_paths)
        return cls(token=token)

    def _set_session(self):
        from slack_sdk import AsyncWebClient, WebClient

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
        url = get_url(context_paths=context_paths)
        return cls(url=url)

    def _set_session(self):
        from slack_sdk import AsyncWebhookClient, WebhookClient

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
        url = get_url(context_paths=context_paths)
        method = get_method(context_paths=context_paths)
        session_attrs = get_session_attrs(context_paths=context_paths)
        return cls(url=url, method=method, session_attrs=session_attrs)
