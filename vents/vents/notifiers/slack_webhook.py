from typing import Dict

from vents.notifiers.spec import NotificationSpec
from vents.notifiers.webhook import WebHookNotifier
from vents.providers.kinds import ProviderKind
from vents.settings import VENTS_CONFIG


class SlackWebHookNotifier(WebHookNotifier):
    notification_key = ProviderKind.SLACK
    name = "Slack WebHook"
    description = "Slack webhooks to send payload to Slack Incoming Webhooks."
    raise_empty_context = True
    validate_keys = ["channel", "icon_url"]

    @classmethod
    def serialize_notification_to_context(cls, notification: NotificationSpec) -> Dict:
        fields = []  # Use build_field

        payload = {
            "fallback": notification.fallback,
            "title": notification.title,
            "title_link": notification.url,
            "text": notification.details,
            "fields": fields,
            "mrkdwn_in": ["text"],
            "footer_icon": VENTS_CONFIG.project_icon,
            "footer": VENTS_CONFIG.project_name,
            "color": notification.color,
            "ts": notification.ts,
        }

        return payload

    @classmethod
    def _prepare(cls, context):
        context = super()._prepare(context)

        data = {
            "fallback": context.get("fallback"),
            "title": context.get("title"),
            "title_link": context.get("title_link"),
            "text": context.get("text"),
            "fields": context.get("fields"),
            "mrkdwn_in": context.get("mrkdwn_in"),
            "footer_icon": context.get("footer_icon"),
            "footer": context.get("footer", VENTS_CONFIG.project_name),
            "color": context.get("color"),
        }
        return {"attachments": [data]}

    @classmethod
    def _pre_execute_web_hook(cls, data, config):
        channel = config.get("channel")
        icon_url = config.get("channel")
        if channel:
            data["channel"] = channel

        if icon_url:
            data["icon_url"] = icon_url

        return data
