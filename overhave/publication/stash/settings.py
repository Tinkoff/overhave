from typing import List

from overhave.publication.settings import BaseGitPublisherSettings
from overhave.storage import FeatureTypeName
from overhave.transport import StashBranch, StashProject, StashRepository, StashReviewer, StashReviewerInfo


class NotSpecifiedFeatureTypeError(RuntimeError):
    """Exception for not specified reviewers relative to feature type."""


class OverhaveStashPublisherSettings(BaseGitPublisherSettings):
    """Settings for :class:`StashVersionPublisher`.

    This is a representation of BitBucket project parameters.
    Some pull-request parameters are also could be defined through these settings.
    """

    repository_name: str  # for example 'bdd-features'
    project_key: str  # for example 'PRJ'

    class Config:
        env_prefix = "OVERHAVE_STASH_"

    @property
    def repository(self) -> StashRepository:
        return StashRepository(slug=self.repository_name, project=StashProject(key=self.project_key))

    @property
    def target_branch(self) -> StashBranch:
        return StashBranch(id=self.default_target_branch_name, repository=self.repository)

    def get_reviewers(self, feature_type: FeatureTypeName) -> List[StashReviewer]:
        if self.feature_type_to_reviewers_mapping:
            reviewers = self.feature_type_to_reviewers_mapping.get(feature_type)
            if not reviewers:
                raise NotSpecifiedFeatureTypeError(
                    f"'{feature_type}' reviewers are not specified in 'feature_type_to_reviewers_mapping' dict!"
                )
        else:
            reviewers = self.default_reviewers
        return [StashReviewer(user=StashReviewerInfo(name=reviewer)) for reviewer in reviewers]
