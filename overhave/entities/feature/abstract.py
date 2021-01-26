import abc
from pathlib import Path
from typing import Dict, List

from overhave.entities.feature.models import FeatureTypeName


class IFeatureExtractor(abc.ABC):
    """ Abstract class for specified project's feature types resolution. """

    @property
    @abc.abstractmethod
    def feature_types(self) -> List[FeatureTypeName]:
        pass

    @property
    @abc.abstractmethod
    def feature_type_to_dir_mapping(self) -> Dict[FeatureTypeName, Path]:
        pass
