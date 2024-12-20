import os

from typing import TYPE_CHECKING, Optional

from vents.providers.base import BaseHttpService, BaseService
from vents.settings import VENTS_CONFIG

if TYPE_CHECKING:
    from vents.connections.connection import Connection


class RedditService(BaseService):
    client_id: Optional[str]
    client_secret: Optional[str]
    user_agent: Optional[str]
    username: Optional[str]
    password: Optional[str]

    @classmethod
    def load_from_connection(
        cls, connection: Optional["Connection"]
    ) -> Optional["RedditService"]:
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

        client_id = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["REDDIT_CLIENT_ID"],
        )
        client_secret = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["REDDIT_CLIENT_SECRET"],
        )
        user_agent = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["REDDIT_USER_AGENT"],
        )
        username = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["REDDIT_USERNAME"],
        )
        password = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["REDDIT_PASSWORD"],
        )
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password,
        )

    def _set_session(self):
        import praw

        self._session = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            username=self.username,
            password=self.password,
        )

    def set_env_vars(self):
        if self.client_id:
            os.environ["REDDIT_CLIENT_ID"] = self.client_id
        if self.client_secret:
            os.environ["REDDIT_CLIENT_SECRET"] = self.client_secret
        if self.user_agent:
            os.environ["REDDIT_USER_AGENT"] = self.user_agent
        if self.username:
            os.environ["REDDIT_USERNAME"] = self.username
        if self.password:
            os.environ["REDDIT_PASSWORD"] = self.password


class RedditRssService(BaseHttpService):
    url: Optional[str] = "https://www.reddit.com/r/{subreddit}.rss"

    @classmethod
    def load_from_connection(
        cls,
        connection: Optional["Connection"] = None,
    ) -> Optional["RedditRssService"]:
        context_paths = []
        if connection:
            if connection.secret and connection.secret.url:
                context_paths.append(connection.secret.url)
        kwargs = {}
        url = VENTS_CONFIG.read_keys(
            context_paths=context_paths, keys=["REDDIT_RSS_URL"]
        )
        if url:
            kwargs["url"] = url
        return cls(**kwargs)
