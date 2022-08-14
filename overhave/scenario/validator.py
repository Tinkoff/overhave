import logging
from pathlib import Path
from typing import List

from overhave.entities import BaseFileExtractor, GitRepositoryInitializer, OverhaveFileSettings
from overhave.scenario import StrictFeatureParsingError
from overhave.scenario.parser import NullableFeatureIdError, ScenarioParser

logger = logging.getLogger(__name__)


class BaseFeatureValidatorException(Exception):
    """Base exception for :class:`FeatureValidator`."""


class FeaturesWithoutIDPresenceError(BaseFeatureValidatorException):
    """Exception for situation with nullable ID features presence."""


class IncorrectFeaturesPresenceError(BaseFeatureValidatorException):
    """Exception for situation with incorrect features presence."""


class FeatureValidator(BaseFileExtractor):
    """Class for features validation."""

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        scenario_parser: ScenarioParser,
        git_initializer: GitRepositoryInitializer,
    ):
        super().__init__(extenstion=file_settings.feature_suffix)
        self._file_settings = file_settings
        self._scenario_parser = scenario_parser
        self._git_initializer = git_initializer

        self._scenario_parser.set_strict_mode(True)
        self._nullable_id_features: List[Path] = []
        self._incorrect_features: List[Path] = []

    def validate(self, raise_if_nullable_id: bool = False, pull_repository: bool = False) -> None:
        if pull_repository:
            self._git_initializer.pull()
        logger.info("Start validation...")
        all_features = self._extract_recursively(self._file_settings.features_dir)
        for feature_file in all_features:
            logger.info("Read feature from file %s...", feature_file.as_posix())
            try:
                feature_info = self._scenario_parser.parse(feature_file.read_text())
            except NullableFeatureIdError:
                logger.warning("Feature has not got suitable Overhave ID!")
                self._nullable_id_features.append(feature_file)
            except StrictFeatureParsingError:
                logger.exception("Feature has incorrect format!")
                self._incorrect_features.append(feature_file)
            else:
                logger.info("Feature successfully parsed: %s", feature_info)
        if self._incorrect_features:
            raise IncorrectFeaturesPresenceError(
                f"Features with incorrect format: {[x.as_posix() for x in self._incorrect_features]}"
            )
        if raise_if_nullable_id and self._nullable_id_features:
            raise FeaturesWithoutIDPresenceError(
                f"Features without IDs: {[x.as_posix() for x in self._nullable_id_features]}"
            )
        logger.info("All features are correct")
