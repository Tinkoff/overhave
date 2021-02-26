from typing import List, Mapping

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities.feature import FeatureTypeName
from overhave.entities.stash.errors import NotSpecifiedFeatureTypeError
from overhave.transport import StashBranch, StashProject, StashRepository, StashReviewer, StashReviewerInfo


class OverhaveStashManagerSettings(BaseOverhavePrefix):
    """ Settings for :class:`StashProjectManager`.

    This is a representation of BitBucket project parameters.
    Some pull-request parameters are also could be defined through these settings.
    """

    repository_name: str  # for example 'bdd-features'
    project_key: str  # for example 'PRJ'
    default_target_branch_name: str = "master"

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
