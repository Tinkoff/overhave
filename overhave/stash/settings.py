from typing import Optional

from pydantic import BaseSettings, validator
from pydantic.datetime_parse import timedelta
from yarl import URL

from overhave.stash.models import StashBranch, StashProject, StashRepository, StashReviewer, StashReviewerInfo


class StashProjectSettings(BaseSettings):
    repository_name: str  # for example 'bdd-features'
    key: str  # for example 'PRJ'
    default_target_branch_name: str = 'master'
    default_reviewer: str

    class Config:
        env_prefix = "STASH_PROJECT_"

    @property
    def repository(self) -> StashRepository:
        return StashRepository(slug=self.repository_name, project=StashProject(key=self.key))

    @property
    def target_branch(self) -> StashBranch:
        return StashBranch(id=self.default_target_branch_name, repository=self.repository)

    @property
    def reviewer(self) -> StashReviewer:
        return StashReviewer(user=StashReviewerInfo(name=self.default_reviewer))


class StashClientSettings(BaseSettings):
    url: URL  # for example "https://my.company"
    pr_path: str = "rest/api/1.0/projects/{project_key}/repos/{repository_name}/pull-requests"

    connect_timeout: timedelta = timedelta(seconds=5)
    read_timeout: timedelta = timedelta(seconds=10)

    auth_token: str

    @validator('url', pre=True)
    def make_url(cls, v: Optional[str]) -> Optional[URL]:
        if v is not None and isinstance(v, str):
            return URL(v)
        return v

    def get_pr_url(self, project_key: str, repository_name: str) -> URL:
        return self.url / self.pr_path.format(project_key=project_key, repository_name=repository_name)

    class Config:
        env_prefix = "STASH_CLIENT_"
