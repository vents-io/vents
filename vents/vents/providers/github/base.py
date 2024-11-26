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
    keys = keys or ["GITHUB_TOKEN"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore


def get_host(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
) -> Optional[str]:
    keys = keys or ["GITHUB_HOST"]
    return VENTS_CONFIG.read_keys(context_paths=context_paths, keys=keys)  # type: ignore
