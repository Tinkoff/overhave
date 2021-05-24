from yarl import URL

from overhave.transport.http import BaseHttpClientSettings


class OverhaveGitlabClientSettings(BaseHttpClientSettings):
    """ Settings for :class:`GitlabHttpClient`. """

    mr_path: str = "/api/v4/projects/{project_key}%2F{repository_name}/merge_requests"
    auth_token: str

    class Config:
        env_prefix = "OVERHAVE_GITLAB_"

    def get_mr_url(self, project_key: str, repository_name: str) -> URL:
        return self.url / self.mr_path.format(project_key=project_key, repository_name=repository_name)
