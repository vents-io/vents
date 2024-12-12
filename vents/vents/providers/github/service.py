import os

from typing import TYPE_CHECKING, Optional

from vents.providers.base import BaseService
from vents.settings import VENTS_CONFIG

if TYPE_CHECKING:
    from vents.connections.connection import Connection


class GithubService(BaseService):
    token: Optional[str] = None
    host: Optional[str] = None

    @classmethod
    def load_from_connection(
        cls, connection: Optional["Connection"] = None
    ) -> Optional["GithubService"]:
        # Check if there are mounting based on secrets/configmaps
        context_paths = []
        schema = None
        builtin_env = None
        if connection:
            if connection.secret and connection.secret.token:
                context_paths.append(connection.secret.token)
            if connection.config_map and connection.config_map.host:
                context_paths.append(connection.config_map.host)
            if connection.schema_:
                schema = connection.get_schema_as_dict()
            if connection.env:
                builtin_env = connection.env

        token = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["GITHUB_TOKEN"],
        )
        host = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["GITHUB_HOST"],
        )
        return cls(token=token, host=host)

    def _set_session(self):
        kwargs = {"base_url": self.host} if self.host else {}
        from github import Github

        self._session = Github(login_or_token=self.token, **kwargs)

    def set_env_vars(self):
        if self.token:
            os.environ["GITHUB_TOKEN"] = self.token
