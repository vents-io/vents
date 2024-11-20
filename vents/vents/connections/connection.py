from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Literal

from clipped.compact.pydantic import Field, StrictStr
from clipped.config.schema import BaseSchemaModel
from clipped.types.ref_or_obj import RefField

from vents.connections.connection_resource import ConnectionResource
from vents.connections.connection_schema import ConnectionSchema
from vents.providers.kinds import ProviderKind


class Connection(BaseSchemaModel):
    _IDENTIFIER = "connection"

    name: StrictStr
    kind: ProviderKind
    is_alias: Optional[bool] = Field(alias="isAlias", exclude=True, default=None)
    description: Optional[StrictStr] = None
    tags: Optional[Union[List[StrictStr], RefField]] = None
    schema_: Optional[ConnectionSchema] = Field(alias="schema", default=None)
    secret: Optional[Union[ConnectionResource, RefField]] = None
    config_map: Optional[Union[ConnectionResource, RefField]] = Field(
        alias="configMap", default=None
    )
    env: Optional[
        Union[Dict[str, Any], List[Union[Tuple[str, str], List[str]]], RefField]
    ] = None
    annotations: Optional[Union[Dict, RefField]] = None

    @classmethod
    def from_model(cls, model) -> "Connection":
        schema = model.schema_
        secret = model.secret
        config_map = model.config_map
        if hasattr(schema, "to_dict"):
            schema = schema.to_dict()
        if hasattr(secret, "to_dict"):
            secret = secret.to_dict()
        if hasattr(config_map, "to_dict"):
            config_map = config_map.to_dict()
        return Connection.from_dict(
            {
                "name": model.name,
                "kind": model.kind,
                "schema": schema,
                "secret": secret,
                "configMap": config_map,
                "env": model.env,
                "annotations": model.annotations,
            }
        )

    @property
    def store_path(self) -> str:
        if self.is_mount:
            return self.schema_.mount_path.rstrip("/")
        if self.is_bucket:
            bucket = self.schema_.bucket.rstrip("/")
            if self.is_wasb:
                from clipped import types

                from vents.settings import VENTS_CONFIG

                return VENTS_CONFIG.config_parser.parse(types.WASB)(
                    key="schema", value=bucket
                ).get_container_path()
            return bucket

    @property
    def is_mount(self) -> bool:
        return ProviderKind.is_mount(self.kind)

    @property
    def is_artifact(self) -> bool:
        return ProviderKind.is_artifact(self.kind)

    @property
    def is_host_path(self) -> bool:
        return ProviderKind.is_host_path(self.kind)

    @property
    def is_volume_claim(self) -> bool:
        return ProviderKind.is_volume_claim(self.kind)

    @property
    def is_bucket(self) -> bool:
        return ProviderKind.is_bucket(self.kind)

    @property
    def is_gcs(self) -> bool:
        return self.kind == ProviderKind.GCS

    @property
    def is_s3(self) -> bool:
        return self.kind == ProviderKind.S3

    @property
    def is_wasb(self) -> bool:
        return ProviderKind.is_wasb(self.kind)

    @staticmethod
    def get_requested_resources(
        resources: List[ConnectionResource],
        connections: List["Connection"],
        resource_key: Literal["secret", "config_map"],
    ) -> List[ConnectionResource]:
        resources = resources or []

        connections = connections or []
        # Create a set of all resources:
        #   * resources request by non managed connections
        #   * resources requested directly by the user
        requested_resources = [r for r in resources if r.is_requested]
        resource_ids = {s.name for s in requested_resources}
        for connection in connections:
            resource = getattr(connection, resource_key)
            if resource and resource.name not in resource_ids:
                resource_ids.add(resource.name)
                requested_resources.append(resource)

        return requested_resources
