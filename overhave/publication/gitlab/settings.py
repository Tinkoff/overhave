from typing import List, Mapping

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities import FeatureTypeName
from overhave.transport.http.gitlab_client import GitlabRepository


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
    default_reviewers: List[str] = []

    # Merge-request default reviewers as mapping with :class:```FeatureTypeName```
    feature_type_to_reviewers_mapping: Mapping[FeatureTypeName, List[str]] = {}

    class Config:
        env_prefix = "OVERHAVE_GITLAB_"

    @property
    def repository(self) -> GitlabRepository:
        return GitlabRepository(project_id=self.repository_id)

    @property
    def target_branch(self) -> str:
        return self.default_target_branch_name

    def get_reviewers(self, feature_type: FeatureTypeName) -> List[str]:
        if self.feature_type_to_reviewers_mapping:
            reviewers = self.feature_type_to_reviewers_mapping.get(feature_type)
            if not reviewers:
                raise NotSpecifiedFeatureTypeError(
                    f"'{feature_type}' reviewers are not specified in 'feature_type_to_reviewers_mapping' dict!"
                )
            return reviewers
        return self.default_reviewers
