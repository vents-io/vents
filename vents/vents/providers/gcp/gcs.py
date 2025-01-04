from typing import Optional

from gcsfs import GCSFileSystem as BaseGCSFileSystem

from vents.providers.gcp.service import GCPService


class GCSFileSystem(BaseGCSFileSystem):
    retries = 5

    async def set_session(self):
        return await self._set_session()


class GCSService(GCPService):
    def _set_session(
        self,
        asynchronous: Optional[bool] = False,
        use_listings_cache: Optional[bool] = False,
        **kwargs,
    ):
        self._session = GCSFileSystem(
            project=self.project_id,
            token=self.credentials,
            asynchronous=asynchronous,
            use_listings_cache=use_listings_cache,
            **kwargs,
        )

    def get_fs(
        self,
        asynchronous: Optional[bool] = False,
        use_listings_cache: Optional[bool] = False,
        **kwargs,
    ):
        self._set_session(
            asynchronous=asynchronous, use_listings_cache=use_listings_cache, **kwargs
        )
        return self.session
