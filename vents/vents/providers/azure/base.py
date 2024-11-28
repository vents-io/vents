import logging
import os

from typing import List, Optional, Union

from vents.settings import VENTS_CONFIG

logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.storage").setLevel(logging.WARNING)
logging.getLogger("azure.storage.blob").setLevel(logging.WARNING)


def get_account_name(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AZURE_ACCOUNT_NAME"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_account_key(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AZURE_ACCOUNT_KEY"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_connection_string(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AZURE_CONNECTION_STRING"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_sas_token(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AZURE_SAS_TOKEN", "AZURE_STORAGE_SAS_TOKEN"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_tenant_id(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AZURE_TENANT_ID"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_client_id(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AZURE_CLIENT_ID"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_client_secret(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AZURE_CLIENT_SECRET"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def set_env_vars(
    account_name: Optional[str] = None,
    account_key: Optional[str] = None,
    connection_string: Optional[str] = None,
):
    if account_name:
        os.environ["AZURE_ACCOUNT_NAME"] = account_name
    if account_key:
        os.environ["AZURE_ACCOUNT_KEY"] = account_key
    if connection_string:
        os.environ["AZURE_CONNECTION_STRING"] = connection_string
