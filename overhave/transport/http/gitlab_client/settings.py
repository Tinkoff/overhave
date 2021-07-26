from typing import Optional

from pydantic import validator
from yarl import URL

from overhave.transport.http import BaseHttpClientSettings
from overhave.transport.http.gitlab_client.utils import TokenType
from overhave.utils import make_url


class OverhaveGitlabClientSettings(BaseHttpClientSettings):
    """ Settings for :class:`GitlabHttpClient`. """

    auth_token: str
    repository_id: str
    token_type: TokenType
    token: str

    @validator("tokenizer_url", pre=True)
    def make_url(cls, v: Optional[str]) -> Optional[URL]:
        return make_url(v)

    class Config:
        env_prefix = "OVERHAVE_GITLAB_"
