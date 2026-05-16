from unittest import TestCase
from unittest.mock import patch

from clipped.utils.tz import now
from vents.notifiers.spec import NotificationSpec
from vents.notifiers.webhook import WebHookNotifier
from vents.providers.kinds import ProviderKind
from vents.settings import VENTS_CONFIG


class TestWebHookNotification(TestCase):
    webhook = WebHookNotifier

    def setUp(self):
        super().setUp()
        self.notification = NotificationSpec(
            title="test",
            description="test",
            details="test",
            fallback="test",
            color="test",
            url="https://test.local",
            ts=now(),
        )

    def test_attrs(self):
        assert self.webhook.notification_key == ProviderKind.WEBHOOK
        assert self.webhook.name == "WebHook"

    def test_validate_empty_config(self):
        assert self.webhook._validate_config({}) == []
        assert self.webhook._validate_config([]) == []
        assert self.webhook._validate_config({"foo": "bar"}) == []

    def test_validate_config_raises_for_wrong_configs(self):
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook._validate_config({"url": "bar"})

        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook._validate_config(
                {"url": "http://foo.com/webhook", "method": 1}
            )

        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook._validate_config(
                {"url": "http://foo.com/webhook", "method": "foo"}
            )

    def test_validate_config(self):
        assert self.webhook._validate_config(
            {"url": "http://foo.com/webhook", "method": "post"}
        ) == [{"url": "http://foo.com/webhook", "method": "POST"}]

        assert self.webhook._validate_config(
            [
                {"url": "http://foo.com/webhook", "method": "post"},
                {"url": "http://bar.com/webhook", "method": "GET"},
            ]
        ) == [
            {"url": "http://foo.com/webhook", "method": "POST"},
            {"url": "http://bar.com/webhook", "method": "GET"},
        ]

    def test_get_empty_config(self):
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook.get_config()
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook.get_config({})
        assert self.webhook.get_config({"foo": "bar"}) == []

    def test_get_config(self):
        assert self.webhook.get_config(
            {"url": "http://foo.com/webhook", "method": "post"}
        ) == [{"url": "http://foo.com/webhook", "method": "POST"}]
        assert self.webhook.get_config(
            [
                {"url": "http://foo.com/webhook", "method": "post"},
                {"url": "http://bar.com/webhook", "method": "GET"},
            ]
        ) == [
            {"url": "http://foo.com/webhook", "method": "POST"},
            {"url": "http://bar.com/webhook", "method": "GET"},
        ]

    def test_prepare(self):
        assert self.webhook._prepare(None) is None
        assert self.webhook._prepare({}) == {}
        assert self.webhook._prepare({"foo": "bar"}) == {"foo": "bar"}

    def test_execute_empty_payload(self):
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook.execute(notification=self.notification)

    def test_execute_empty_payload_with_config(self):
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook.execute(
                notification=None,
                config={"url": "http://bar.com/webhook", "method": "GET"},
            )

    def test_execute_payload_with_config(self):
        with patch("vents.notifiers.webhook.safe_request") as mock_execute:
            self.webhook.execute(
                notification=self.notification,
                config={"url": "http://bar.com/webhook", "method": "GET"},
            )

        assert mock_execute.call_count == 1

    def test_execute(self):
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook.execute(notification=self.notification)

        with patch("vents.notifiers.webhook.safe_request") as mock_execute:
            self.webhook.execute(
                notification=self.notification,
                config={"url": "http://bar.com/webhook", "method": "GET"},
            )

        assert mock_execute.call_count == 1
