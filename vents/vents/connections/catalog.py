from typing import Dict, List, Optional

from clipped.compact.pydantic import PrivateAttr
from clipped.config.schema import BaseSchemaModel

from vents.connections.connection import Connection
from vents.connections.connection_resource import ConnectionResource


class ConnectionCatalog(BaseSchemaModel):
    connections: Optional[List[Connection]] = None
    _all_connections: List[Connection] = PrivateAttr()
    _secrets: Optional[List[ConnectionResource]] = PrivateAttr(default=None)
    _config_maps: Optional[List[ConnectionResource]] = PrivateAttr(default=None)
    _connections_by_names: Dict[str, Connection] = PrivateAttr()

    def __init__(
        self,
        **data,
    ):
        super().__init__(**data)
        # Post init
        self._all_connections = []
        self._connections_by_names = {}
        self._secrets = None
        self._config_maps = None
        self.set_all_connections()

    def set_all_connections(self) -> None:
        self._all_connections = self.connections[:] if self.connections else []
        self._connections_by_names = {}
        self._secrets = None
        self._config_maps = None

    @property
    def all_connections(self) -> List[Connection]:
        return self._all_connections

    @property
    def secrets(self) -> List[ConnectionResource]:
        if self._secrets or not self._all_connections:
            return self._secrets
        secret_names = set()
        secrets = []
        for c in self._all_connections:
            if c.secret and c.secret.name not in secret_names:
                secret_names.add(c.secret.name)
                secrets.append(c.secret)
        self._secrets = secrets
        return self._secrets

    @property
    def config_maps(self) -> List[ConnectionResource]:
        if self._config_maps or not self._all_connections:
            return self._config_maps
        config_map_names = set()
        config_maps = []
        for c in self._all_connections:
            if c.config_map and c.config_map.name not in config_map_names:
                config_map_names.add(c.config_map.name)
                config_maps.append(c.config_map)
        self._config_maps = config_maps
        return self._config_maps

    @property
    def connections_by_names(self) -> Dict[str, Connection]:
        if self._connections_by_names or not self._all_connections:
            return self._connections_by_names

        self._connections_by_names = {c.name: c for c in self._all_connections}
        return self._connections_by_names
