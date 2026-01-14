from requests import RequestException
from typing import Dict, List

from clipped.utils.requests import safe_request

from vents.notifiers.base import BaseNotifier
from vents.notifiers.spec import NotificationSpec
from vents.providers.kinds import ProviderKind
from vents.settings import VENTS_CONFIG


class WebHookNotifier(BaseNotifier):
    notification_key = ProviderKind.WEBHOOK
    name = "WebHook"
    description = (
        "Webhooks send an HTTP payload to the webhook's configured URL."
        "Webhooks can be used automatically "
        "by subscribing to certain events, "
        "or manually triggered by a user operation."
    )
    raise_empty_context = False

    @classmethod
    def serialize_notification_to_context(cls, notification: NotificationSpec) -> Dict:
        context = {
            "context": notification.context,
            "title": notification.title,
            "details": notification.details,
            "finished_at": notification.ts,
        }
        return context

    @classmethod
    def _pre_execute_web_hook(cls, data: Dict, config: Dict) -> Dict:
        return data

    @classmethod
    def _execute(
        cls,
        data: Dict,
        config: List[Dict],
        validate_url_security: bool = False,
    ) -> None:
        for web_hook in config:
            data = cls._pre_execute_web_hook(data=data, config=web_hook)
            try:
                if web_hook["method"] == "POST":
                    safe_request(
                        url=web_hook["url"],
                        method=web_hook["method"],
                        json=data,
                        validate_url_security=validate_url_security,
                    )
                else:
                    safe_request(
                        url=web_hook["url"],
                        method=web_hook["method"],
                        params=data,
                        validate_url_security=validate_url_security,
                    )
            except RequestException:
                VENTS_CONFIG.logger.warning(
                    "Could not send web hook, exception.", exc_info=True
                )
