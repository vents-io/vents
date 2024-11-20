from typing import List, Optional

from clipped.compact.pydantic import Field, StrictStr
from clipped.config.schema import BaseSchemaModel


class ConnectionResource(BaseSchemaModel):
    _IDENTIFIER = "connection_resource"

    name: StrictStr
    mount_path: Optional[StrictStr] = Field(alias="mountPath", default=None)
    host_path: Optional[StrictStr] = Field(alias="hostPath", default=None)
    items: Optional[List[StrictStr]] = None
    default_mode: Optional[str] = Field(alias="defaultMode", default=None)
    is_requested: Optional[bool] = Field(alias="isRequested", default=None)
