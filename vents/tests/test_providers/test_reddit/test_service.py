import os

from unittest import TestCase
from unittest.mock import MagicMock, patch

from vents.config import AppConfig
from vents.providers.reddit.service import RedditRssService, RedditService


class TestRedditService(TestCase):
    def setUp(self):
        self.client_id = "test-client-id"
        self.client_secret = "test-client-secret"
        self.user_agent = "test-user-agent"
        self.username = "test-username"
        self.password = "test-password"

    def test_init(self):
        service = RedditService(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            username=self.username,
            password=self.password,
        )
        self.assertEqual(service.client_id, self.client_id)
        self.assertEqual(service.client_secret, self.client_secret)
        self.assertEqual(service.user_agent, self.user_agent)
        self.assertEqual(service.username, self.username)
        self.assertEqual(service.password, self.password)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret(self, mock_read_keys):
        mock_read_keys.side_effect = [
            self.client_id,
            self.client_secret,
            self.user_agent,
            self.username,
            self.password,
        ]

        mock_connection = MagicMock()
        mock_connection.secret.mount_path = "/path/to/secret"
        mock_connection.schema_ = None
        mock_connection.env = None
        mock_connection.config_map = None

        service = RedditService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.client_id, self.client_id)
        self.assertEqual(service.client_secret, self.client_secret)
        self.assertEqual(service.user_agent, self.user_agent)
        self.assertEqual(service.username, self.username)
        self.assertEqual(service.password, self.password)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_without_connection(self, mock_read_keys):
        mock_read_keys.side_effect = [
            self.client_id,
            self.client_secret,
            self.user_agent,
            self.username,
            self.password,
        ]

        service = RedditService.load_from_connection(connection=None)

        self.assertEqual(service.client_id, self.client_id)
        self.assertEqual(service.client_secret, self.client_secret)
        self.assertEqual(service.user_agent, self.user_agent)
        self.assertEqual(service.username, self.username)
        self.assertEqual(service.password, self.password)

    @patch("praw.Reddit")
    def test_set_session(self, mock_reddit):
        service = RedditService(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            username=self.username,
            password=self.password,
        )
        service._set_session()

        mock_reddit.assert_called_once_with(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            username=self.username,
            password=self.password,
        )

    def test_set_env_vars(self):
        service = RedditService(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            username=self.username,
            password=self.password,
        )
        service.set_env_vars()

        self.assertEqual(os.environ.get("REDDIT_CLIENT_ID"), self.client_id)
        self.assertEqual(os.environ.get("REDDIT_CLIENT_SECRET"), self.client_secret)
        self.assertEqual(os.environ.get("REDDIT_USER_AGENT"), self.user_agent)
        self.assertEqual(os.environ.get("REDDIT_USERNAME"), self.username)
        self.assertEqual(os.environ.get("REDDIT_PASSWORD"), self.password)


class TestRedditRssService(TestCase):
    def setUp(self):
        self.url = "https://www.reddit.com/r/test.rss"
        self.default_url = "https://www.reddit.com/r/{subreddit}.rss"

    def test_init(self):
        service = RedditRssService(url=self.url)
        self.assertEqual(service.url, self.url)

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_with_secret(self, mock_read_keys):
        mock_read_keys.return_value = self.url

        mock_connection = MagicMock()
        mock_connection.secret.url = "/path/to/url"

        service = RedditRssService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.url, self.url)
        mock_read_keys.assert_called_once_with(
            context_paths=["/path/to/url"], keys=["REDDIT_RSS_URL"]
        )

    @patch.object(AppConfig, "read_keys")
    def test_load_from_connection_without_connection(self, mock_read_keys):
        mock_read_keys.return_value = None

        service = RedditRssService.load_from_connection(connection=None)

        self.assertEqual(service.url, self.default_url)
        mock_read_keys.assert_called_once_with(
            context_paths=[], keys=["REDDIT_RSS_URL"]
        )
