import abc
import logging
from pathlib import Path
from typing import Dict, List

from overhave.entities.settings import OverhaveFileSettings

logger = logging.getLogger(__name__)


class FeatureTypeExtractionError(RuntimeError):
    """ Exception for feature type extraction error. """

    pass


class IFeatureExtractor(abc.ABC):
    """ Abstract class for specified project's feature types resolution. """

    @property
    @abc.abstractmethod
    def feature_types(self) -> List[str]:
        pass

    @property
    @abc.abstractmethod
    def feature_type_to_dir_mapping(self) -> Dict[str, Path]:
        pass


class FeatureExtractor(IFeatureExtractor):
    """ Class for specified project's feature types resolution. """

    def __init__(self, file_settings: OverhaveFileSettings):
        self._file_settings = file_settings

        self._feature_types: List[str] = []
        self._feature_type_to_dir_mapping: Dict[str, Path] = {}
        try:
            self._extract_project_data()
        except FeatureTypeExtractionError:
            logger.exception("Extraction error while trying to collect features!")

    def _extract_project_data(self) -> None:
        feature_type_dirs = [
            d
            for d in self._file_settings.features_base_dir.iterdir()
            if all(
                (d.is_dir(), d != self._file_settings.tmp_dir, not d.name.startswith("."), not d.name.startswith("_"))
            )
        ]
        if not feature_type_dirs:
            raise FeatureTypeExtractionError(
                f"Could not find any subdirectory in features base directory '{self._file_settings.features_base_dir}'!"
            )
        self._feature_types = [t.name for t in feature_type_dirs]
        logger.info("Registered feature types: %s", self._feature_types)
        self._feature_type_to_dir_mapping = {t.name: t for t in feature_type_dirs}

    @property
    def feature_types(self) -> List[str]:
        return self._feature_types

    @property
    def feature_type_to_dir_mapping(self) -> Dict[str, Path]:
        return self._feature_type_to_dir_mapping
