import os

from typing import TYPE_CHECKING, Optional

from clipped.utils.json import orjson_dumps

from vents.providers.base import BaseService
from vents.settings import VENTS_CONFIG

if TYPE_CHECKING:
    from vents.connections.connection import Connection


class OpenAIService(BaseService):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_async: bool = False
    kwargs: Optional[dict] = None

    @classmethod
    def load_from_connection(
        cls, connection: Optional["Connection"] = None
    ) -> Optional["OpenAIService"]:
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

        api_key = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["OPENAI_API_KEY"],
        )
        base_url = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["OPENAI_BASE_URL"],
        )
        kwargs = VENTS_CONFIG.read_keys(
            context_paths=context_paths,
            schema=schema,
            env=builtin_env,
            keys=["OPENAI_KWARGS"],
        )
        return cls(
            api_key=api_key,
            base_url=base_url,
            kwargs=kwargs,
        )

    def _set_session(self):
        import openai

        kwargs = self.kwargs or {}
        self._session = (
            openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                **kwargs,
            )
            if self.is_async
            else openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                **kwargs,
            )
        )

    def set_env_vars(self):
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key
        if self.base_url:
            os.environ["OPENAI_BASE_URL"] = self.base_url
        if self.kwargs:
            os.environ["OPENAI_KWARGS"] = orjson_dumps(self.kwargs)
