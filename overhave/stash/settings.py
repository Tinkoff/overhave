from typing import List, Mapping, Optional

from pydantic import validator
from pydantic.datetime_parse import timedelta
from yarl import URL

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities.feature import FeatureTypeName
from overhave.stash.errors import NotSpecifiedFeatureTypeError
from overhave.stash.models import StashBranch, StashProject, StashRepository, StashReviewer, StashReviewerInfo


class OverhaveStashProjectSettings(BaseOverhavePrefix):
    """ Settings for :class:`StashProjectManager`.

    This is a representation of BitBucket project parameters.
    Some pull-request parameters are also could be defined through these settings.
    """

    repository_name: str  # for example 'bdd-features'
    project_key: str  # for example 'PRJ'
    default_target_branch_name: str = 'master'

    # Pull-request default reviewers as list
    default_reviewers: List[str] = []
    # Pull-request default reviewers as mapping with :class:```FeatureTypeName```
    feature_type_to_reviewers_mapping: Mapping[FeatureTypeName, List[str]] = {}

    @property
    def repository(self) -> StashRepository:
        return StashRepository(slug=self.repository_name, project=StashProject(key=self.project_key))

    @property
    def target_branch(self) -> StashBranch:
        return StashBranch(id=self.default_target_branch_name, repository=self.repository)

    def get_reviewers(self, feature_type: FeatureTypeName) -> List[StashReviewer]:
        if self.feature_type_to_reviewers_mapping:
            reviewers = self.feature_type_to_reviewers_mapping[feature_type]
            if not reviewers:
                raise NotSpecifiedFeatureTypeError(
                    f"FeatureTypeName '{feature_type}' key was not specified in "
                    "'feature_type_to_reviewers_mapping' dict!"
                )
        else:
            reviewers = self.default_reviewers
        return [StashReviewer(user=StashReviewerInfo(name=reviewer)) for reviewer in reviewers]


class OverhaveStashClientSettings(BaseOverhavePrefix):
    """ Settings for :class:`StashClient`. """

    stash_url: URL  # for example "https://my.company"
    pr_path: str = "rest/api/1.0/projects/{project_key}/repos/{repository_name}/pull-requests"

    connect_timeout: timedelta = timedelta(seconds=5)
    read_timeout: timedelta = timedelta(seconds=10)

    auth_token: str

    @validator('stash_url', pre=True)
    def make_url(cls, v: Optional[str]) -> Optional[URL]:
        if v is not None and isinstance(v, str):
            return URL(v)
        return v

    def get_pr_url(self, project_key: str, repository_name: str) -> URL:
        return self.stash_url / self.pr_path.format(project_key=project_key, repository_name=repository_name)
