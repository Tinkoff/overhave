from typing import Any, Dict, Optional

from pydantic import validator
from yarl import URL

from overhave.transport.http import BaseHttpClientSettings
from overhave.utils import make_url


class TokenizerClientSettings(BaseHttpClientSettings):
    """ Important environments and settings for :class:`TokenizerClient`. """

    enabled: bool = False
    url: Optional[URL] = None  # type: ignore
    initiator: Optional[str] = None
    vault_server_name: Optional[str] = None

    class Config:
        env_prefix = "GITLAB_TOKENIZER_"

    @validator("vault_server_name", "initiator")
    def validate_vault_server_name(cls, v: Optional[str], values: Dict[str, Any]):
        if values["enabled"] and not isinstance(v, str):
            raise ValueError("Please verify GITLAB_TOKENIZER_VAULT_SERVER_NAME! Maybe you've forgotten about this env!")
        return v

    @validator("url")
    def make_url(cls, v: Optional[str], values: Dict[str, Any]):
        if values["enabled"] and v is None:
            raise ValueError("Please verify url for tokenizator! Maybe you've forgotten about this env!")
        return make_url(v)
