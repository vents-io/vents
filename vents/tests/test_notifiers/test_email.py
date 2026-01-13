from unittest import TestCase
from unittest.mock import MagicMock, patch

from clipped.utils.tz import now

from vents.notifiers.email import EmailNotifier
from vents.notifiers.spec import NotificationSpec
from vents.providers.kinds import ProviderKind
from vents.settings import VENTS_CONFIG


class TestEmailNotifier(TestCase):
    notifier = EmailNotifier

    def setUp(self):
        super().setUp()
        self.notification = NotificationSpec(
            title="Test Alert",
            description="Test description",
            details="Test details message",
            fallback="test",
            color="#FF0000",
            url="https://test.local",
            ts=now(),
        )
        self.valid_config = {
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "user@example.com",
            "smtp_password": "password",
            "from_email": "noreply@example.com",
            "recipients": ["user1@example.com", "user2@example.com"],
            "use_tls": True,
        }

    def test_attrs(self):
        assert self.notifier.notification_key == ProviderKind.EMAIL
        assert self.notifier.name == "Email"

    def test_validate_empty_config(self):
        assert self.notifier._validate_config({}) == []
        assert self.notifier._validate_config([]) == []
        assert self.notifier._validate_config(None) == []

    def test_validate_config_missing_smtp_host(self):
        config = {"recipients": ["user@example.com"]}
        assert self.notifier._validate_config(config) == []

    def test_validate_config_missing_recipients(self):
        config = {"smtp_host": "smtp.example.com"}
        assert self.notifier._validate_config(config) == []

    def test_validate_config_valid(self):
        result = self.notifier._validate_config(self.valid_config)

        assert len(result) == 1
        assert result[0]["smtp_host"] == "smtp.example.com"
        assert result[0]["smtp_port"] == 587
        assert result[0]["smtp_user"] == "user@example.com"
        assert result[0]["smtp_password"] == "password"
        assert result[0]["from_email"] == "noreply@example.com"
        assert result[0]["recipients"] == ["user1@example.com", "user2@example.com"]
        assert result[0]["use_tls"] is True
        assert result[0]["use_ssl"] is False

    def test_validate_config_defaults(self):
        config = {
            "smtp_host": "smtp.example.com",
            "recipients": ["user@example.com"],
        }
        result = self.notifier._validate_config(config)

        assert len(result) == 1
        assert result[0]["smtp_port"] == 587  # Default
        assert result[0]["from_email"] == "noreply@polyaxon.com"  # Default
        assert result[0]["use_tls"] is True  # Default
        assert result[0]["use_ssl"] is False  # Default

    def test_validate_config_list(self):
        configs = [
            {"smtp_host": "smtp1.example.com", "recipients": ["user1@example.com"]},
            {"smtp_host": "smtp2.example.com", "recipients": ["user2@example.com"]},
        ]
        result = self.notifier._validate_config(configs)

        assert len(result) == 2
        assert result[0]["smtp_host"] == "smtp1.example.com"
        assert result[1]["smtp_host"] == "smtp2.example.com"

    def test_serialize_notification_to_context(self):
        context = self.notifier.serialize_notification_to_context(self.notification)

        assert context["subject"] == "Test Alert"
        assert context["body_text"] == "Test details message"
        assert "body_html" in context
        assert "Test Alert" in context["body_html"]
        assert "Test description" in context["body_html"]

    def test_build_html_body(self):
        html = self.notifier._build_html_body(self.notification)

        assert "Test Alert" in html
        assert "Test description" in html
        assert "Test details message" in html
        assert "#FF0000" in html  # Color
        assert "https://test.local" in html  # URL

    def test_build_html_body_without_url(self):
        notification = NotificationSpec(
            title="Test",
            description="Desc",
            details="Details",
        )
        html = self.notifier._build_html_body(notification)

        assert "View Details" not in html

    def test_prepare(self):
        with self.assertRaises(VENTS_CONFIG.exception):
            self.notifier._prepare(None)
        with self.assertRaises(VENTS_CONFIG.exception):
            self.notifier._prepare({})

        context = {"subject": "Test Subject", "body_text": "Test body"}
        result = self.notifier._prepare(context)

        assert result["subject"] == "Test Subject"
        assert result["body_text"] == "Test body"

    def test_prepare_default_subject(self):
        context = {"body_text": "Test body"}
        result = self.notifier._prepare(context)

        assert result["subject"] == "Notification"

    @patch("vents.notifiers.email.smtplib.SMTP")
    def test_send_email_with_tls(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        self.notifier._send_email(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_password="password",
            from_email="noreply@example.com",
            recipients=["user@example.com"],
            subject="Test",
            body_text="Test body",
            use_tls=True,
            use_ssl=False,
        )

        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "password")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("vents.notifiers.email.smtplib.SMTP_SSL")
    def test_send_email_with_ssl(self, mock_smtp_ssl):
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server

        self.notifier._send_email(
            smtp_host="smtp.example.com",
            smtp_port=465,
            smtp_user="user@example.com",
            smtp_password="password",
            from_email="noreply@example.com",
            recipients=["user@example.com"],
            subject="Test",
            body_text="Test body",
            use_tls=False,
            use_ssl=True,
        )

        mock_smtp_ssl.assert_called_once_with("smtp.example.com", 465)
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("vents.notifiers.email.smtplib.SMTP")
    def test_send_email_without_auth(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        self.notifier._send_email(
            smtp_host="smtp.example.com",
            smtp_port=25,
            smtp_user=None,
            smtp_password=None,
            from_email="noreply@example.com",
            recipients=["user@example.com"],
            subject="Test",
            body_text="Test body",
            use_tls=False,
            use_ssl=False,
        )

        mock_server.login.assert_not_called()
        mock_server.sendmail.assert_called_once()

    @patch("vents.notifiers.email.EmailNotifier._send_email")
    def test_execute(self, mock_send_email):
        data = {"subject": "Test", "body_text": "Body", "body_html": "<p>Body</p>"}
        config = [self.valid_config]

        self.notifier._execute(data, config)

        mock_send_email.assert_called_once()
        call_kwargs = mock_send_email.call_args
        assert call_kwargs[1]["smtp_host"] == "smtp.example.com"
        assert call_kwargs[1]["subject"] == "Test"
        assert call_kwargs[1]["body_text"] == "Body"

    @patch("vents.notifiers.email.EmailNotifier._send_email")
    def test_execute_multiple_configs(self, mock_send_email):
        data = {"subject": "Test", "body_text": "Body"}
        configs = [
            {
                "smtp_host": "smtp1.example.com",
                "smtp_port": 587,
                "from_email": "a@a.com",
                "recipients": ["b@b.com"],
            },
            {
                "smtp_host": "smtp2.example.com",
                "smtp_port": 587,
                "from_email": "c@c.com",
                "recipients": ["d@d.com"],
            },
        ]

        self.notifier._execute(data, configs)

        assert mock_send_email.call_count == 2
