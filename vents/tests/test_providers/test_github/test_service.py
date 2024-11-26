import os

from unittest import TestCase
from unittest.mock import MagicMock, patch

from vents.providers.github.service import GithubService


class TestGithubService(TestCase):
    def setUp(self):
        self.token = "test-github-token"
        self.host = "https://github.enterprise.com/api/v3"

    def test_init(self):
        service = GithubService(token=self.token, host=self.host)
        self.assertEqual(service.token, self.token)
        self.assertEqual(service.host, self.host)

    @patch("vents.providers.github.service.get_token")
    @patch("vents.providers.github.service.get_host")
    def test_load_from_connection_with_secret_and_config(
        self, mock_get_host, mock_get_token
    ):
        mock_get_token.return_value = self.token
        mock_get_host.return_value = self.host
        mock_connection = MagicMock()
        mock_connection.secret.token = "/path/to/secret/token"
        mock_connection.config_map.host = "/path/to/config/host"

        service = GithubService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.token, self.token)
        self.assertEqual(service.host, self.host)
        mock_get_token.assert_called_once_with(
            context_paths=["/path/to/secret/token", "/path/to/config/host"]
        )
        mock_get_host.assert_called_once_with(
            context_paths=["/path/to/secret/token", "/path/to/config/host"]
        )

    @patch("vents.providers.github.service.get_token")
    @patch("vents.providers.github.service.get_host")
    def test_load_from_connection_with_secret_only(self, mock_get_host, mock_get_token):
        mock_get_token.return_value = self.token
        mock_get_host.return_value = None

        mock_connection = MagicMock()
        mock_connection.secret.token = "/path/to/secret/token"
        mock_connection.config_map = None

        service = GithubService.load_from_connection(connection=mock_connection)

        self.assertEqual(service.token, self.token)
        self.assertIsNone(service.host)
        mock_get_token.assert_called_once_with(context_paths=["/path/to/secret/token"])
        mock_get_host.assert_called_once_with(context_paths=["/path/to/secret/token"])

    @patch("vents.providers.github.service.get_token")
    @patch("vents.providers.github.service.get_host")
    def test_load_from_connection_without_connection(
        self, mock_get_host, mock_get_token
    ):
        mock_get_token.return_value = self.token
        mock_get_host.return_value = None

        service = GithubService.load_from_connection(connection=None)

        self.assertEqual(service.token, self.token)
        self.assertIsNone(service.host)
        mock_get_token.assert_called_once_with(context_paths=[])
        mock_get_host.assert_called_once_with(context_paths=[])

    @patch("github.Github")
    def test_set_session_without_host(self, mock_github_client):
        service = GithubService(token=self.token)
        service._set_session()

        mock_github_client.assert_called_once_with(login_or_token=self.token)

    @patch("github.Github")
    def test_set_session_with_host(self, mock_github_client):
        service = GithubService(token=self.token, host=self.host)
        service._set_session()

        mock_github_client.assert_called_once_with(
            login_or_token=self.token, base_url=self.host
        )

    def test_set_env_vars(self):
        service = GithubService(token=self.token)
        service.set_env_vars()
        self.assertEqual(os.environ.get("GITHUB_TOKEN"), self.token)

    def test_set_env_vars_no_token(self):
        os.environ["GITHUB_TOKEN"] = "test"
        self.assertIn("GITHUB_TOKEN", os.environ)
        os.environ.pop("GITHUB_TOKEN")
        service = GithubService(token=None)
        service.set_env_vars()
        self.assertNotIn("GITHUB_TOKEN", os.environ)
