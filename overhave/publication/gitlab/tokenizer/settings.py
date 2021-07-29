from typing import Any, Dict, Optional

from pydantic import validator
from yarl import URL

from overhave.transport.http import BaseHttpClientSettings


class TokenizerClientSettings(BaseHttpClientSettings):
    """ Important environments and settings for :class:`TokenizerClient`. """

    enabled: bool = False
    url: URL = URL("https://overhave.readthedocs.io/not-a-handler")
    initiator: Optional[str] = None
    vault_server_name: Optional[str] = None

    class Config:
        env_prefix = "GITLAB_TOKENIZER_"

    @validator("vault_server_name", "initiator")
    def validate_vault_server_name(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values["enabled"] and not isinstance(v, str):
            raise ValueError("Please verify GITLAB_TOKENIZER_VAULT_SERVER_NAME! Maybe you've forgotten about this env!")
        return v
