from yarl import URL

from overhave.transport.http import BaseHttpClientSettings


class OverhaveGitlabClientSettings(BaseHttpClientSettings):
    """ Settings for :class:`GitlabHttpClient`. """

    mr_path: str = "api/v4/projects/{repository_id}/merge_requests"
    auth_token: str

    class Config:
        env_prefix = "OVERHAVE_GITLAB_"

    def get_mr_url(self, repository_id: str) -> URL:
        return self.url / self.mr_path.format(repository_name=repository_id)
