import os

from typing import TYPE_CHECKING, Optional

from vents.providers.azure.base import (
    get_account_key,
    get_account_name,
    get_client_id,
    get_client_secret,
    get_connection_string,
    get_sas_token,
    get_tenant_id,
)
from vents.providers.base import BaseService

if TYPE_CHECKING:
    from vents.connections.connection import Connection


class AzureService(BaseService):
    account_name: Optional[str]
    account_key: Optional[str]
    connection_string: Optional[str]
    sas_token: Optional[str]
    tenant_id: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]

    @classmethod
    def load_from_connection(
        cls, connection: Optional["Connection"] = None
    ) -> Optional["AzureService"]:
        # Check if there are mounting based on secrets/configmaps
        context_paths = []
        schema = None
        builtin_env = None
        if connection:
            if connection.secret and connection.secret.mount_path:
                context_paths.append(connection.secret.mount_path)
            if connection.config_map and connection.config_map.mount_path:
                context_paths.append(connection.config_map.mount_path)
            if connection.schema_:
                schema = connection.get_schema_as_dict()
            if connection.env:
                builtin_env = connection.env

        account_name = get_account_name(
            context_paths=context_paths, schema=schema, env=builtin_env
        )
        account_key = get_account_key(
            context_paths=context_paths, schema=schema, env=builtin_env
        )
        connection_string = get_connection_string(
            context_paths=context_paths, schema=schema, env=builtin_env
        )
        sas_token = get_sas_token(
            context_paths=context_paths, schema=schema, env=builtin_env
        )
        tenant_id = get_tenant_id(
            context_paths=context_paths, schema=schema, env=builtin_env
        )
        client_id = get_client_id(
            context_paths=context_paths, schema=schema, env=builtin_env
        )
        client_secret = get_client_secret(
            context_paths=context_paths, schema=schema, env=builtin_env
        )
        return cls(
            account_name=account_name,
            account_key=account_key,
            connection_string=connection_string,
            sas_token=sas_token,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secre=client_secret,
        )

    def set_env_vars(self):
        if self._account_name:
            os.environ["AZURE_ACCOUNT_NAME"] = self._account_name
        if self._account_key:
            os.environ["AZURE_ACCOUNT_KEY"] = self._account_key
        if self._connection_string:
            os.environ["AZURE_CONNECTION_STRING"] = self._connection_string
