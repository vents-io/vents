import os

from typing import Any, Dict, List, Optional, Union

from clipped.utils.lists import to_list
from clipped.utils.urls import validate_url

from vents.notifiers.spec import NotificationSpec
from vents.settings import VENTS_CONFIG

ConfigType = Union[Dict, List[Dict]]


class BaseNotifier:
    notification_key = None
    name = None
    description = ""
    raise_empty_context = True
    check_config = True
    validate_keys = None

    @classmethod
    def _validate_config(cls, config: ConfigType) -> ConfigType:
        """Validate that a given config is valid for the current config."""
        if not config:
            return []
        args = cls.validate_keys or []
        return cls._get_valid_config(config, *args)

    @classmethod
    def _get_valid_config(cls, config, *fields) -> ConfigType:
        config = to_list(config)
        web_hooks = []
        for web_hook in config:
            if not web_hook.get("url"):
                VENTS_CONFIG.logger.warning(
                    "Settings contains a non compatible web hook: `%s`", web_hook
                )
                continue

            url = web_hook["url"]
            if not validate_url(url):
                raise VENTS_CONFIG.exception(
                    "{} received invalid URL `{}`.".format(cls.name, url)
                )

            method = web_hook.get("method", "POST")
            if not isinstance(method, str):
                raise VENTS_CONFIG.exception(
                    "{} received invalid method `{}`.".format(cls.name, method)
                )

            _method = method.upper()
            if _method not in ["GET", "POST"]:
                raise VENTS_CONFIG.exception(
                    "{} received non compatible method `{}`.".format(cls.name, method)
                )

            result_web_hook = {"url": url, "method": _method}
            for field in fields:
                if field in web_hook:
                    result_web_hook[field] = web_hook[field]
            web_hooks.append(result_web_hook)

        return web_hooks

    @classmethod
    def _get_config(
        cls,
    ) -> ConfigType:  # TODO: Move to service to get from catalog/env var
        """Getting config to execute an action.

        Currently we get config from env vars.

        should be a list of urls and potentially a method.

        If no method is given, then by default we use POST.
        """
        value = os.environ.get(cls.notification_key)
        if not value:
            raise VENTS_CONFIG.exception(
                "Could not validate config for notifier {}".format(cls.name)
            )

        return VENTS_CONFIG.config_parser.parse(Dict)(
            key=cls.notification_key, value=value, is_list=True
        )

    @classmethod
    def get_config(cls, config: ConfigType = None) -> ConfigType:
        config = config or cls._get_config()
        config = cls._validate_config(config)
        return config

    @classmethod
    def _prepare(cls, context: Dict) -> Dict:
        """This is where you should alter the context to fit the action.

        Default behavior will leave the context as it is.
        """
        if not context and cls.raise_empty_context:
            raise VENTS_CONFIG.exception(
                "{} received invalid payload context.".format(cls.name)
            )

        return context

    @classmethod
    def _execute(cls, data: Dict, config: Optional[ConfigType], **kwargs) -> None:
        raise NotImplementedError

    @classmethod
    def serialize_notification_to_context(cls, notification: NotificationSpec) -> Dict:
        """Implementation for turning a notification info into actionable notification."""

    @classmethod
    def execute(
        cls,
        notification: NotificationSpec,
        config: Optional[ConfigType] = None,
        **kwargs,
    ) -> Any:
        if not notification:
            raise VENTS_CONFIG.exception(
                "Received an invalid run `{}`.".format(notification)
            )
        context = cls.serialize_notification_to_context(notification=notification)
        config = cls.get_config(config=config)
        if cls.check_config and not config:
            return False

        data = cls._prepare(context)
        try:
            result = cls._execute(data=data, config=config, **kwargs)
        except Exception as e:
            VENTS_CONFIG.logger.error(
                "Exception during the execution of the notifier %s. Error: %s",
                cls.name,
                e,
                exc_info=True,
            )
            return
        return result
