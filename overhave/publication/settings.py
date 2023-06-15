from typing import Mapping, TypeVar

from overhave.base_settings import BaseOverhavePrefix
from overhave.publication.objects import PublicationManagerType
from overhave.storage import FeatureTypeName


class BaseGitPublisherSettings(BaseOverhavePrefix):
    """Base git publisher settings."""

    default_reviewers: list[str] = []
    feature_type_to_reviewers_mapping: Mapping[FeatureTypeName, list[str]] = {}
    default_target_branch_name: str = "master"
    pull_before_creating_mr_enabled: bool = True


class PublicationSettings(BaseOverhavePrefix):
    """Publication settings where you can specify publication manager and its behavior."""

    # Choose gitlab or stash as a publication manager
    publication_manager_type: PublicationManagerType = PublicationManagerType.GITLAB


GitPublisherSettings = TypeVar("GitPublisherSettings", bound=BaseGitPublisherSettings)
