from typing import Any

from pydantic import BaseSettings, root_validator


class OverhaveS3ManagerSettings(BaseSettings):
    """Settings for S3Client."""

    enabled: bool = False

    url: str | None
    region_name: str | None
    access_key: str | None
    secret_key: str | None
    verify: bool = True

    autocreate_buckets: bool = False

    class Config:
        env_prefix = "OVERHAVE_S3_"

    @root_validator
    def validate_enabling(cls, values: dict[str, Any]) -> dict[str, Any]:
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
