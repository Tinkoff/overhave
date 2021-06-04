from typing import List, Mapping

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities.feature import FeatureTypeName
from overhave.transport.http.gitlab_client import GitlabBranch, GitlabRepository, GitlabReviewer, GitlabReviewerInfo


class NotSpecifiedFeatureTypeError(RuntimeError):
    """ Exception for not specified reviewers relative to feature type. """


class OverhaveGitlabPublisherSettings(BaseOverhavePrefix):
    """ Settings for :class:`GitlabVersionPublisher`.

    This is a representation of Gitlab project parameters.
    Some merge-request parameters are also could be defined through these settings.
    """

    repository_id: str  # for example '2034'
    default_target_branch_name: str = "master"

    # Pull-request default reviewers as list
    default_reviewers: List[str] = []
    # Pull-request default reviewers as mapping with :class:```FeatureTypeName```
    feature_type_to_reviewers_mapping: Mapping[FeatureTypeName, List[str]] = {}

    @property
    def repository(self) -> GitlabRepository:
        return GitlabRepository(slug=self.repository_id)

    @property
    def target_branch(self) -> GitlabBranch:
        return GitlabBranch(id=self.default_target_branch_name, repository=self.repository)

    def get_reviewers(self, feature_type: FeatureTypeName) -> List[GitlabReviewer]:
        if self.feature_type_to_reviewers_mapping:
            reviewers = self.feature_type_to_reviewers_mapping[feature_type]
            if not reviewers:
                raise NotSpecifiedFeatureTypeError(
                    f"'{feature_type}' reviewers are not specified in " "'feature_type_to_reviewers_mapping' dict!"
                )
        else:
            reviewers = self.default_reviewers
        return [GitlabReviewer(user=GitlabReviewerInfo(name=reviewer)) for reviewer in reviewers]
