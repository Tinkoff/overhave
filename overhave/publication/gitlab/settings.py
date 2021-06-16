from typing import List, Mapping

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities import FeatureTypeName
from overhave.transport.http.gitlab_client import GitlabBranch, GitlabRepository
from overhave.transport.http.gitlab_client.models import GitlabReviewer, GitlabReviewerInfo


class NotSpecifiedFeatureTypeError(RuntimeError):
    """ Exception for not specified reviewers relative to feature type. """


class OverhaveGitlabPublisherSettings(BaseOverhavePrefix):
    """ Settings for :class:`GitlabVersionPublisher`.

    This is a representation of Gitlab project parameters.
    Some merge-request parameters are also could be defined through these settings.
    """

    repository_id: str  # for example '2034'
    default_target_branch_name: str = "master"

    # Merge-request default reviewers as list
    default_reviewers: List[int] = []

    # Merge-request default reviewers as mapping with :class:```FeatureTypeName```
    feature_type_to_reviewers_mapping: Mapping[FeatureTypeName, List[int]] = {}

    @property
    def repository(self) -> GitlabRepository:
        return GitlabRepository(project_id=self.repository_id)

    @property
    def target_branch(self) -> GitlabBranch:
        return GitlabBranch(project_id=self.repository_id, branch=self.default_target_branch_name)

    def get_reviewers(self, feature_type: FeatureTypeName) -> List[GitlabReviewer]:
        if self.feature_type_to_reviewers_mapping:
            reviewers = self.feature_type_to_reviewers_mapping.get(feature_type)
            if not reviewers:
                raise NotSpecifiedFeatureTypeError(
                    f"'{feature_type}' reviewers are not specified in " "'feature_type_to_reviewers_mapping' dict!"
                )
        else:
            reviewers = self.default_reviewers
        return [GitlabReviewer(user=GitlabReviewerInfo(id=reviewer_id)) for reviewer_id in reviewers]
