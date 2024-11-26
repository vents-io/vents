from typing import List, Optional, Union

from vents.settings import VENTS_CONFIG


def get_token(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    **kwargs,
) -> Optional[str]:
    value = kwargs.get("token")
    if value:
        return value
    keys = keys or ["DISCORD_TOKEN"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore


def get_webhook_url(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    **kwargs,
) -> Optional[str]:
    value = kwargs.get("url")
    if value:
        return value
    keys = keys or ["DISCORD_WEBHOOK_URL"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore


def get_discord_intents(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    **kwargs,
) -> Optional[str]:
    value = kwargs.get("intents")
    if value:
        return value
    keys = keys or ["DISCORD_INTENTS"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore
