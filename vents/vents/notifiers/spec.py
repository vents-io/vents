from datetime import datetime
from typing import Dict, Optional

from clipped.config.schema import BaseSchemaModel
from clipped.types import Uri


class NotificationSpec(BaseSchemaModel):
    title: str
    description: str
    details: str
    fallback: Optional[str] = None
    context: Optional[Dict] = None
    url: Optional[Uri] = None
    color: Optional[str] = None
    ts: Optional[datetime] = None
