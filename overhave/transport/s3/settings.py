from typing import Any, Dict, Optional

from pydantic import BaseSettings, root_validator


class S3ManagerSettings(BaseSettings):
    """ Settings for S3Client. """

    enabled: bool = False
    url: Optional[str]
    region_name: Optional[str]
    access_key: Optional[str]
    secret_key: Optional[str]
    verify: bool = True

    class Config:
        env_prefix = "OVERHAVE_S3_"

    @root_validator
    def validate_enabling(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        enabled = values.get("enabled")
        if enabled and not all(
            (
                isinstance(values.get("url"), str),
                isinstance(values.get("access_key"), str),
                isinstance(values.get("secret_key"), str),
            )
        ):
            raise ValueError("Url, access key and secret key should be specified!")
        return values
