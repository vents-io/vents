import abc

from typing import TYPE_CHECKING, Any, Optional

from clipped.compact.pydantic import PrivateAttr
from clipped.config.schema import BaseSchemaModel

if TYPE_CHECKING:
    from vents.connections.catalog import ConnectionCatalog
    from vents.connections.connection import Connection


class BaseService(BaseSchemaModel):
    _session: Optional[Any] = PrivateAttr(default=None)

    class Config:
        extra = "allow"

    @classmethod
    def load_from_catalog(
        cls, connection_name: str, catalog: Optional["ConnectionCatalog"]
    ) -> Optional["BaseService"]:
        """Loads a new service from the catalog."""
        connection = cls.get_connection(
            connection_name=connection_name, catalog=catalog
        )
        return cls.load_from_connection(connection=connection)

    @classmethod
    def load_from_connection(
        cls, connection: Optional["Connection"]
    ) -> Optional["BaseService"]:
        raise NotImplementedError

    @staticmethod
    def get_connection(
        connection_name: str, catalog: Optional["ConnectionCatalog"]
    ) -> Optional["Connection"]:
        if not catalog or not connection_name:
            return None
        return catalog.connections_by_names.get(connection_name)

    @property
    def session(self):
        if self._session is None:
            # Create session with defaults
            self._set_session()
        return self._session

    @abc.abstractmethod
    def _set_session(self):
        raise NotImplementedError

    @abc.abstractmethod
    def load_from_connection(self, **kwargs):
        raise NotImplementedError
