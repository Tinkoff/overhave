from overhave.transport.http import BaseHttpClientSettings
from overhave.transport.http.gitlab_client.utils import TokenType


class OverhaveGitlabClientSettings(BaseHttpClientSettings):
    """ Settings for :class:`GitlabHttpClient`. """

    auth_token: str
    repository_id: str
    token_type: TokenType
    token: str

    class Config:
        env_prefix = "OVERHAVE_GITLAB_"
