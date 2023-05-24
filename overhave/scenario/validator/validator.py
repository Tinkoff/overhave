import logging
from pathlib import Path

from overhave.entities import BaseFileExtractor, GitRepositoryInitializer, OverhaveFileSettings
from overhave.scenario.parser import NullableFeatureIdError, ScenarioParser, StrictFeatureParsingError
from overhave.scenario.validator.abstract import IFeatureValidator
from overhave.scenario.validator.duplicate_id_mixin import FeatureDuplicatedIdValidationMixin
from overhave.scenario.validator.errors import FeaturesWithoutIDPresenceError, IncorrectFeaturesPresenceError

logger = logging.getLogger(__name__)


class FeatureValidator(IFeatureValidator, BaseFileExtractor, FeatureDuplicatedIdValidationMixin):
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

        self._nullable_id_features: list[Path] = []
        self._incorrect_features: list[Path] = []

    def validate(self, raise_if_nullable_id: bool = False, pull_repository: bool = False) -> None:
        if pull_repository:
            self._git_initializer.pull()
        logger.info("Start validation...")
        feature_paths = self._extract_recursively(self._file_settings.features_dir)
        for feature_path in feature_paths:
            logger.info("Read feature from file %s...", feature_path.as_posix())
            try:
                feature_info = self._scenario_parser.parse(feature_path.read_text())
                self._save_to_feature_id_to_path_mapping(feature_path=feature_path, feature_id=feature_info.id)
            except NullableFeatureIdError:
                logger.warning("Feature has not got suitable Overhave ID!")
                self._nullable_id_features.append(feature_path)
            except StrictFeatureParsingError:
                logger.exception("Feature has incorrect format!")
                self._incorrect_features.append(feature_path)
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
        self._validate_duplicate_ids()
        logger.info("All features are correct")
