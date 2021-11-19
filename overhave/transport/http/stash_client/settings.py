from yarl import URL

from overhave.transport.http.base_client import BaseHttpClientSettings


class OverhaveStashClientSettings(BaseHttpClientSettings):
    """Settings for :class:`StashHttpClient`."""

    pr_path: str = "rest/api/1.0/projects/{project_key}/repos/{repository_name}/pull-requests"
    auth_token: str

    class Config:
        env_prefix = "OVERHAVE_STASH_"

    def get_pr_url(self, project_key: str, repository_name: str) -> URL:
        return self.url / self.pr_path.format(project_key=project_key, repository_name=repository_name)
