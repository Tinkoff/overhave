from typing import Optional

from yarl import URL

from overhave.transport.http import BaseHttpClientSettings


class S3ClientSettings(BaseHttpClientSettings):
    """ Settings for S3Client. """

    url: URL
    region_name: Optional[str]
    access_key: str
    secret_key: str
    verify: bool = True

    class Config:
        env_prefix = "OVERHAVE_S3_"
