from typing import Optional

from vents.config import AppConfig


VENTS_CONFIG: Optional[AppConfig]


def create_app(config: Optional[AppConfig] = None) -> AppConfig:
    global VENTS_CONFIG

    VENTS_CONFIG = config or AppConfig()
    return VENTS_CONFIG
