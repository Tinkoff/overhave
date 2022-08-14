import logging
from datetime import datetime
from pathlib import Path
from typing import cast

import allure
import pytz

from overhave.entities import BaseFileExtractor, FeatureExtractor, GitRepositoryInitializer, OverhaveFileSettings
from overhave.scenario import FeatureInfo, NullableFeatureIdError, ScenarioParser, StrictFeatureInfo
from overhave.storage import FeatureModel
from overhave.synchronization.abstract import IOverhaveSynchronizer
from overhave.synchronization.storage_manager import SynchronizerStorageManager

logger = logging.getLogger(__name__)


class BaseOverhaveSynchronizerException(Exception):
    """Base exception for :class:`OverhaveSynchronizer`."""


class NullableInfoNameError(BaseOverhaveSynchronizerException):
    """Exception for situation without feature info name."""


class NullableInfoAuthorError(BaseOverhaveSynchronizerException):
    """Exception for situation without feature info author."""


class NullableInfoFeatureTypeError(BaseOverhaveSynchronizerException):
    """Exception for situation without feature info type."""


class OverhaveSynchronizer(BaseFileExtractor, IOverhaveSynchronizer):
    """Class for synchronization between git and database."""

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        scenario_parser: ScenarioParser,
        feature_extractor: FeatureExtractor,
        git_initializer: GitRepositoryInitializer,
        storage_manager: SynchronizerStorageManager,
    ):
        super().__init__(extenstion=file_settings.feature_suffix)
        self._file_settings = file_settings
        self._scenario_parser = scenario_parser
        self._feature_extractor = feature_extractor
        self._git_initializer = git_initializer
        self._storage_manager = storage_manager

    def _update_feature(self, model: FeatureModel, info: StrictFeatureInfo, file_ts: datetime) -> None:
        logger.info("Feature is gonna be updated...")
        self._storage_manager.ensure_users_exist(info)
        model.name = info.name
        model.feature_tags = self._storage_manager.get_feature_tags(info=info)
        model.severity = info.severity
        model.last_edited_by = info.last_edited_by
        model.last_edited_at = file_ts
        model.task = info.tasks
        self._storage_manager.update_db_feature(model=model, scenario=info.scenarios)
        logger.info("Feature has been updated successfully.")

    def _create_feature(self, file: Path, info: FeatureInfo) -> None:
        logger.info("Feature is gonna be created...")
        if info.name is None:
            raise NullableInfoNameError("Feature info has not got feature name!")
        if info.type is None:
            raise NullableInfoFeatureTypeError("Could not create feature without feature type!")
        if info.author is None:
            raise NullableInfoAuthorError("Could not create feature without author!")
        self._storage_manager.ensure_users_exist(info)  # type: ignore
        feature_tags = self._storage_manager.get_feature_tags(info=info)  # type: ignore
        feature_type = self._storage_manager.get_feature_type(info.type)
        if info.last_edited_by is None:
            info.last_edited_by = info.author
        feature_model = FeatureModel(
            id=0,
            name=info.name,
            author=info.author,
            type_id=feature_type.id,
            last_edited_by=info.last_edited_by,
            last_edited_at=info.last_edited_at,
            task=info.tasks or [],
            file_path=file.relative_to(
                self._feature_extractor.feature_type_to_dir_mapping[feature_type.name]
            ).as_posix(),
            released=True,
            feature_type=feature_type,
            feature_tags=feature_tags,
            severity=info.severity or allure.severity_level.NORMAL,
        )
        self._storage_manager.create_db_feature(model=feature_model, scenario=info.scenarios)  # type: ignore
        logger.info("Feature with ID=%s has been created successfully.", feature_model.id)

    def synchronize(self, create_db_features: bool = False, pull_repository: bool = False) -> None:  # noqa: C901
        if pull_repository:
            self._git_initializer.pull()
        logger.info("Start synchronization...")
        all_features = self._extract_recursively(self._file_settings.features_dir)
        for feature_file in all_features:
            logger.info("Synchronize feature from file %s...", feature_file.as_posix())
            feature_text = feature_file.read_text()
            self._scenario_parser.set_strict_mode(True)
            try:
                feature_info: StrictFeatureInfo = cast(StrictFeatureInfo, self._scenario_parser.parse(feature_text))
            except NullableFeatureIdError:
                logger.warning("Feature has not got Overhave ID or ID format is incorrect.")
                if not create_db_features:
                    logger.warning("create_db_features=%s. Skip it.", create_db_features)
                    continue
                self._scenario_parser.set_strict_mode(False)
                optional_feature_info = cast(FeatureInfo, self._scenario_parser.parse(feature_text))
                self._create_feature(file=feature_file, info=optional_feature_info)
                continue
            logger.debug("Parsed feature info: %s", feature_info)
            feature_model = self._storage_manager.get_feature(feature_info.id)
            if feature_model is None:
                logger.warning("Feature doesn't exist in Overhave database.")
                continue  # TODO: unlink file and create MR with deletions at the end

            feature_file_ts = datetime.fromtimestamp(feature_file.stat().st_mtime, tz=pytz.UTC)
            if feature_model.last_edited_at == feature_file_ts and feature_model.released:
                logger.warning("Feature has been already synchronized.")
                continue
            last_change_time = self._storage_manager.get_last_change_time(model=feature_model)
            if last_change_time < feature_file_ts:
                self._update_feature(model=feature_model, info=feature_info, file_ts=feature_file_ts)
                continue
            if feature_model.released:
                logger.info("Feature is already actual. Skip.")
                continue
            logger.warning(
                "Feature was changed soon (at %s), but not released. Skip.",
                last_change_time.strftime("%d-%m-%Y %H:%M:%S"),
            )
        logger.info("Synchronization completed.")
