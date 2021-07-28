from typing import Optional

from overhave.transport.http import BaseHttpClientSettings


class TokenizerClientSettings(BaseHttpClientSettings):
    """ Important environments and settings for :class:`TokenizerClient`. """

    vault_server_name: Optional[str] = None

    class Config:
        env_prefix = "GITLAB_TOKENIZER_"
