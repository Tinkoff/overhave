from typing import Any, Dict, Optional

from pydantic import validator
from yarl import URL

from overhave.transport.http import BaseHttpClientSettings


class TokenizerClientSettings(BaseHttpClientSettings):
    """ Important environments and settings for :class:`TokenizerClient`. """

    enabled: bool = False
    url: Optional[URL] = None  # type: ignore
    initiator: Optional[str] = None
    remote_key: Optional[str] = None
    remote_key_name: Optional[str] = None

    class Config:
        env_prefix = "OVERHAVE_GITLAB_TOKENIZER_"

    @validator("remote_key", "initiator", "remote_key_name")
    def validate_remote_key_and_initiator(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values["enabled"] and not isinstance(v, str):
            raise ValueError(
                "Please verify REMOTE_KEY, REMOTE_KEY_NAME and INITIATOR! Maybe you've forgotten about this env!"
            )
        return v
