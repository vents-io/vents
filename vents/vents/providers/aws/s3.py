from typing import Optional

from s3fs import S3FileSystem as BaseS3FileSystem

from vents.providers.aws.service import AWSService


class S3FileSystem(BaseS3FileSystem):
    retries = 5

    async def _ls(self, path: str, detail: bool = False, force: bool = False):
        return await super()._ls(path, detail=detail, refresh=force)


class S3Service(AWSService):
    def _set_session(
        self,
        asynchronous: Optional[bool] = False,
        use_listings_cache: Optional[bool] = False,
        **kwargs,
    ):
        config_kwargs = kwargs.get("config_kwargs", {})
        if self.region and "region_name" not in config_kwargs:
            config_kwargs["region_name"] = self.region
        client_kwargs = kwargs.get("client_kwargs", {})
        if self.verify_ssl is not None and "verify" not in client_kwargs:
            client_kwargs["verify"] = self.verify_ssl
        self._session = S3FileSystem(
            key=self.access_key_id,
            secret=self.secret_access_key,
            token=self.session_token,
            use_ssl=self.use_ssl,
            endpoint_url=self.endpoint_url,
            config_kwargs=config_kwargs,
            client_kwargs=client_kwargs,
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
            asynchronous=asynchronous,
            use_listings_cache=use_listings_cache,
            **kwargs,
        )
        return self.session
