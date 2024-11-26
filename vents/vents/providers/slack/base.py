from typing import Dict, List, Optional, Union

from vents.settings import VENTS_CONFIG


def get_token(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    **kwargs,
) -> Optional[str]:
    value = kwargs.get("token")
    if value:
        return value
    keys = keys or ["SLACK_TOKEN"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore


def get_url(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    **kwargs,
) -> Optional[str]:
    value = kwargs.get("url")
    if value:
        return value
    keys = keys or ["SLACK_URL"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore


def get_method(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    **kwargs,
) -> Optional[str]:
    value = kwargs.get("method")
    if value:
        return value
    keys = keys or ["SLACK_METHOD"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore


def get_session_attrs(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    **kwargs,
) -> Optional[Dict]:
    value = kwargs.get("session_attrs")
    if value:
        return value
    keys = keys or ["SLACK_SESSION_ATTRS"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore
