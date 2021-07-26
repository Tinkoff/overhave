from typing import Optional

from pydantic import validator
from yarl import URL

from overhave.transport.http import BaseHttpClientSettings
from overhave.utils import make_url


class OverhaveGitlabClientSettings(BaseHttpClientSettings):
    """ Settings for :class:`GitlabHttpClient`. """

    auth_token: str
    repository_id: str
    tokenizer_url: URL
    token_path: str
    vault_server_name: str
    initiator: str

    @validator("tokenizer_url", pre=True)
    def make_url(cls, v: Optional[str]) -> Optional[URL]:
        return make_url(v)

    @property
    def get_token_url(self) -> URL:
        return self.tokenizer_url / self.token_path

    class Config:
        env_prefix = "OVERHAVE_GITLAB_"
