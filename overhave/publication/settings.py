from typing import List, Mapping, TypeVar

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities import FeatureTypeName
from overhave.publication.objects import PublicationManagerType


class BaseGitPublisherSettings(BaseOverhavePrefix):
    """Base git publisher settings."""

    default_reviewers: List[str] = []
    feature_type_to_reviewers_mapping: Mapping[FeatureTypeName, List[str]] = {}
    default_target_branch_name: str = "master"


class PublicationSettings(BaseOverhavePrefix):
    """Publication settings where you can specify publication manager and its behavior."""

    # Choose gitlab or stash as a publication manager
    publication_manager_type: PublicationManagerType = PublicationManagerType.GITLAB


GitPublisherSettings = TypeVar("GitPublisherSettings", bound=BaseGitPublisherSettings)
