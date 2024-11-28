import os

from collections.abc import Mapping
from typing import Dict, List, Optional, Union

import google.auth
import google.oauth2.service_account

from clipped.utils.json import orjson_loads
from google.oauth2.service_account import Credentials

from vents.settings import VENTS_CONFIG

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def get_default_key_path():
    return "{}/.gc/gc-secret.json".format(VENTS_CONFIG.context_path or "/tmp")


def get_project_id(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
    **kwargs,
) -> Optional[str]:
    value = kwargs.get("project_id")
    if value:
        return value
    keys = keys or [
        "GC_PROJECT",
        "GOOGLE_PROJECT",
        "GC_PROJECT_ID",
        "GOOGLE_PROJECT_ID",
    ]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_key_path(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["GC_KEY_PATH", "GOOGLE_KEY_PATH", "GOOGLE_APPLICATION_CREDENTIALS"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_keyfile_dict(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[Dict]:
    keys = keys or ["GC_KEYFILE_DICT", "GOOGLE_KEYFILE_DICT"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_scopes(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[List[str]]:
    keys = keys or ["GC_SCOPES", "GOOGLE_SCOPES"]
    scopes = VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )
    scopes = VENTS_CONFIG.config_parser.parse(str)(
        key="scopes",
        value=scopes,
        is_optional=True,
        is_list=True,
    )
    return scopes or DEFAULT_SCOPES


def get_gc_credentials(
    key_path: Optional[str],
    keyfile_dict: Optional[Union[str, Dict]],
    scopes: Optional[List[str]],
) -> Credentials:
    """
    Returns the Credentials object for Google API
    """
    if not key_path and not keyfile_dict:
        context_secret = get_default_key_path()
        # Look for default GC path
        if os.path.exists(context_secret):
            key_path = context_secret

    if not key_path and not keyfile_dict:
        VENTS_CONFIG.logger.info(
            "Getting connection using `google.auth.default()` "
            "since no key file is defined for hook."
        )
        credentials, _ = google.auth.default(scopes=scopes)
    elif key_path:
        # Get credentials from a JSON file.
        if key_path.endswith(".json"):
            VENTS_CONFIG.logger.info("Getting connection using a JSON key file.")
            credentials = Credentials.from_service_account_file(
                os.path.abspath(key_path), scopes=scopes
            )
        else:
            raise VENTS_CONFIG.exception("Unrecognised extension for key file.")
    else:
        # Get credentials from JSON data.
        try:
            if not isinstance(keyfile_dict, Mapping):
                keyfile_dict = orjson_loads(keyfile_dict)  # type: ignore

            # Convert escaped newlines to actual newlines if any.
            keyfile_dict["private_key"] = keyfile_dict["private_key"].replace(
                "\\n", "\n"
            )

            credentials = Credentials.from_service_account_info(
                keyfile_dict, scopes=scopes
            )
        except ValueError:  # json.decoder.JSONDecodeError does not exist on py2
            raise VENTS_CONFIG.exception("Invalid key JSON.")

    return credentials
