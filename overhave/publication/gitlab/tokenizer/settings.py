from typing import Any, Dict, Optional

import httpx
from pydantic import validator

from overhave.transport.http import BaseHttpClientSettings
from overhave.utils import make_url


class TokenizerClientSettings(BaseHttpClientSettings):
    """Important environments and settings for :class:`TokenizerClient`."""

    enabled: bool = False
    url: Optional[httpx.URL] = None  # type: ignore
    initiator: str = "Overhave"
    remote_key: Optional[str] = None
    remote_key_name: Optional[str] = None

    class Config:
        env_prefix = "OVERHAVE_GITLAB_TOKENIZER_"

    @validator("url", pre=True)
    def make_url(cls, v: Optional[str]) -> Optional[httpx.URL]:
        return make_url(v)

    @validator("url", "remote_key", "remote_key_name")
    def validate_remote_key_and_initiator(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values.get("enabled") and not isinstance(v, str):
            raise ValueError("Please verify that url, remote_key and remote_key_name variables are not nullable!")
        return v
