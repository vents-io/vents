from tests.test_notifiers.test_webhook_notification import TestWebHookNotification
from vents.notifiers.teams_webhook import TeamsWebHookNotifier
from vents.providers.kinds import ProviderKind
from vents.settings import VENTS_CONFIG


class TestTeamsWebHookNotifier(TestWebHookNotification):
    webhook = TeamsWebHookNotifier

    def test_attrs(self):
        assert self.webhook.notification_key == ProviderKind.TEAMS
        assert self.webhook.name == "Teams WebHook"

    def test_prepare(self):
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook._prepare(None)
        with self.assertRaises(VENTS_CONFIG.exception):
            self.webhook._prepare({})

        context = {"title": "Test Title", "text": "Test message", "color": "FF0000"}
        result = self.webhook._prepare(context)

        # Verify MessageCard format
        assert result["@type"] == "MessageCard"
        assert result["@context"] == "http://schema.org/extensions"
        assert result["summary"] == "Test Title"
        assert result["title"] == "Test Title"
        assert result["themeColor"] == "FF0000"
        assert len(result["sections"]) == 1
        assert result["sections"][0]["text"] == "Test message"
        assert result["sections"][0]["markdown"] is True

    def test_prepare_with_url(self):
        context = {
            "title": "Test Title",
            "text": "Test message",
            "url": "https://example.com/details",
        }
        result = self.webhook._prepare(context)

        # Should have potentialAction with OpenUri
        assert "potentialAction" in result
        assert len(result["potentialAction"]) == 1
        assert result["potentialAction"][0]["@type"] == "OpenUri"
        assert result["potentialAction"][0]["name"] == "View Details"
        assert (
            result["potentialAction"][0]["targets"][0]["uri"]
            == "https://example.com/details"
        )

    def test_prepare_without_url(self):
        context = {"title": "Test Title", "text": "Test message"}
        result = self.webhook._prepare(context)

        # Should not have potentialAction
        assert "potentialAction" not in result

    def test_prepare_default_color(self):
        context = {"title": "Test Title", "text": "Test message"}
        result = self.webhook._prepare(context)

        # Should have default blue color
        assert result["themeColor"] == "0076D7"

    def test_serialize_notification_to_context(self):
        context = self.webhook.serialize_notification_to_context(self.notification)

        assert context["title"] == self.notification.title
        assert context["text"] == self.notification.details
        assert context["color"] == self.notification.color
        assert context["url"] == str(self.notification.url)


del TestWebHookNotification
