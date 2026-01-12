from typing import Dict

from vents.notifiers.spec import NotificationSpec
from vents.notifiers.webhook import WebHookNotifier
from vents.providers.kinds import ProviderKind
from vents.settings import VENTS_CONFIG


class TeamsWebHookNotifier(WebHookNotifier):
    notification_key = ProviderKind.TEAMS
    name = "Teams WebHook"
    description = "Microsoft Teams webhooks to send payload to Teams channels."
    raise_empty_context = True

    @classmethod
    def serialize_notification_to_context(cls, notification: NotificationSpec) -> Dict:
        return {
            "title": notification.title,
            "text": notification.details,
            "url": str(notification.url) if notification.url else None,
            "color": notification.color,
        }

    @classmethod
    def _prepare(cls, context: Dict) -> Dict:
        context = super()._prepare(context)

        # Microsoft Teams Message Card format
        # https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": context.get("title", "Notification"),
            "themeColor": context.get("color", "0076D7"),
            "title": context.get("title", "Notification"),
            "sections": [
                {
                    "activityTitle": VENTS_CONFIG.project_name,
                    "activityImage": VENTS_CONFIG.project_icon,
                    "text": context.get("text", ""),
                    "markdown": True,
                }
            ],
        }

        # Add action button if URL provided
        url = context.get("url")
        if url:
            payload["potentialAction"] = [
                {
                    "@type": "OpenUri",
                    "name": "View Details",
                    "targets": [{"os": "default", "uri": url}],
                }
            ]

        return payload