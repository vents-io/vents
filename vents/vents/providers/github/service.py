import os

from typing import TYPE_CHECKING, Optional

from vents.providers.base import BaseService
from vents.providers.github.base import get_host, get_token

if TYPE_CHECKING:
    from vents.connections.connection import Connection


class GithubService(BaseService):
    token: Optional[str] = None
    host: Optional[str] = None

    @classmethod
    def load_from_connection(
        cls, connection: Optional["Connection"]
    ) -> Optional["GithubService"]:
        # Check if there are mounting based on secrets/configmaps
        context_paths = []
        if connection:
            if connection.secret and connection.secret.token:
                context_paths.append(connection.secret.token)
            if connection.config_map and connection.config_map.host:
                context_paths.append(connection.config_map.host)
        token = get_token(context_paths=context_paths)
        host = get_host(context_paths=context_paths)
        return cls(token=token, host=host)

    def _set_session(self):
        kwargs = {"base_url": self.host} if self.host else {}
        from github import Github

        self._session = Github(login_or_token=self.token, **kwargs)

    def set_env_vars(self):
        if self.token:
            os.environ["GITHUB_TOKEN"] = self.token
