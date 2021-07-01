from overhave.transport.http import BaseHttpClientSettings


class OverhaveGitlabClientSettings(BaseHttpClientSettings):
    """ Settings for :class:`GitlabHttpClient`. """

    auth_token: str
    repository_id: str

    class Config:
        env_prefix = "OVERHAVE_GITLAB_"
