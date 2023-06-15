import abc
from pathlib import Path

from overhave.storage import FeatureTypeName


class IFeatureExtractor(abc.ABC):
    """Abstract class for specified project's feature types resolution."""

    @property
    @abc.abstractmethod
    def feature_types(self) -> list[FeatureTypeName]:
        pass

    @property
    @abc.abstractmethod
    def feature_type_to_dir_mapping(self) -> dict[FeatureTypeName, Path]:
        pass
