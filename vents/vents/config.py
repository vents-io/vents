import logging
import os

from typing import Any, Dict, List, Optional, Set, Type, Union

from clipped.compact.pydantic import Field
from clipped.config.parser import ConfigParser
from clipped.config.schema import BaseSchemaModel
from clipped.types import Uri
from clipped.utils.paths import check_dirname_exists

from vents.connections import ConnectionCatalog
from vents.connections.connection import Connection
from vents.exceptions import VentError

_logger = logging.getLogger("vents.config.reader")


class AppConfig(BaseSchemaModel):
    project_name: Optional[str] = "Vents"
    project_url: Optional[Uri] = ""
    project_icon: Optional[Uri] = ""
    env_prefix: Optional[str] = "VENTS"
    context_path: Optional[str] = ""
    logger: Any = _logger
    exception: Type[Exception] = VentError
    config_parser: Type[ConfigParser] = Field(
        default=ConfigParser, alias="config_parser"
    )
    catalog: Optional[ConnectionCatalog] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.catalog = self.catalog or self.load_connections_catalog()

    def read_keys_from_env(
        self, keys: Union[Set[str], List[str], str], env: Optional[Dict] = None
    ) -> Optional[Any]:
        """
        Returns a variable from one of the list of keys based on the os.env.
        Args:
            keys: list(str). list of keys to check in the environment

        Returns:
            str | None
        """
        env = env or os.environ
        keys = keys or []
        if not isinstance(keys, (list, tuple, set)):
            keys = [keys]
        for key in keys:
            value = env.get(key)
            if value:
                if value.lower() == "true":
                    return True
                if value.lower() == "false":
                    return False
                return value
            # Prepend prefix if set
            if self.env_prefix:
                key = "{}_{}".format(self.env_prefix, key)
                value = env.get(key)
                if value:
                    return value

        return None

    def read_keys_from_path(
        self, context_paths: List[str], keys: Union[Set[str], List[str], str]
    ) -> Optional[Any]:
        """
        Returns a variable from one of the list of keys based on a base path.
        Args:
            context_paths: List[str], base path where to look for keys.
            keys: list(str). list of keys to check in the environment

        Returns:
            str | None
        """
        context_paths = context_paths or []
        context_paths = [
            c
            for c in context_paths
            if check_dirname_exists(c, is_dir=True, reraise=False)
        ]
        if not context_paths:
            return None

        keys = keys or []
        if not isinstance(keys, (list, tuple, set)):
            keys = [keys]  # type: ignore
        for key in keys:
            for context_path in context_paths:
                key_path = os.path.join(context_path, key)
                if not os.path.exists(key_path):
                    continue
                with open(key_path) as f:
                    value = f.read()
                    if value:
                        if value.lower() == "true":
                            return True
                        if value.lower() == "false":
                            return False
                        return value

        return None

    def read_keys_from_schema(
        self, schema: Dict, keys: Union[Set[str], List[str], str]
    ) -> Optional[Any]:
        """Reads keys from a schema

        Args:
            schema: Dict. schema to read keys from
            keys: list(str). list of keys to check in the environment

        Returns:
            str | None
        """
        if not schema:
            return None
        keys = keys or []
        if not isinstance(keys, (list, tuple, set)):
            keys = [keys]  # type: ignore
        for key in keys:
            value = schema.get(key)
            if value:
                if value.lower() == "true":
                    return True
                if value.lower() == "false":
                    return False
                return value

    def get_connections_catalog_env_name(self) -> str:
        env_name = "CONNECTIONS_CATALOG"
        if self.env_prefix:
            env_name = "{}_{}".format(self.env_prefix, env_name)
        return env_name

    @staticmethod
    def get_connections_catalog(
        connections: Optional[List[Connection]],
    ) -> Optional[ConnectionCatalog]:
        if not connections:
            return None
        return ConnectionCatalog(connections=connections)

    def set_connections_catalog(self, connections: Optional[List[Connection]]):
        self.catalog = self.get_connections_catalog(connections)

    def load_connections_catalog(self) -> Optional[ConnectionCatalog]:
        catalog_env_name = self.get_connections_catalog_env_name()
        connections_catalog = os.environ.get(catalog_env_name)
        if not connections_catalog:
            return None
        return ConnectionCatalog.read(connections_catalog, config_type=".json")

    def get_connection_for(self, name: Optional[str]) -> Optional[Connection]:
        """Checks if a connection has a mount path exported"""
        if not name or not self.catalog:
            return None

        return self.catalog.connections_by_names.get(name)

    def read_keys(
        self,
        keys: List[str],
        schema: Optional[Dict] = None,
        env: Optional[Dict] = None,
        context_paths: Optional[List[str]] = None,
    ) -> Optional[Any]:
        """Returns a variable by checking first a context path and then in the environment."""
        keys = (
            {k.lower() for k in keys}
            | {k.upper() for k in keys}
            | {"".join(k.lower().split("_")) for k in keys}
        )
        if context_paths:
            value = self.read_keys_from_path(context_paths=context_paths, keys=keys)
            if value is not None:
                return value
        if schema:
            value = self.read_keys_from_schema(schema=schema, keys=keys)
            if value is not None:
                return value
        if env:
            value = self.read_keys_from_env(keys=keys, env=env)
            if value is not None:
                return value
        return self.read_keys_from_env(keys=keys)
