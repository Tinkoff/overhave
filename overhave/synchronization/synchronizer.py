import logging
from datetime import datetime
from pathlib import Path
from typing import List

import allure
import pytz

from overhave.entities import BaseFileExtractor, FeatureExtractor, GitRepositoryInitializer, OverhaveFileSettings
from overhave.scenario import FeatureInfo, ScenarioParser
from overhave.storage import (
    FeatureModel,
    IDraftStorage,
    IFeatureStorage,
    IFeatureTagStorage,
    IFeatureTypeStorage,
    IScenarioStorage,
    ISystemUserStorage,
    ScenarioModel,
    TagModel,
)
from overhave.synchronization.abstract import IOverhaveSynchronizer

logger = logging.getLogger(__name__)


class BaseOverhaveSynchronizerException(Exception):
    """Base exception for :class:`OverhaveSynchronizer`."""


class NullableLastEditedAtError(BaseOverhaveSynchronizerException):
    """Exception for nullable last_edited_at."""


class NullableInfoLastEditedByError(BaseOverhaveSynchronizerException):
    """Exception for nullable feature info last_edited_at."""


class NullableInfoNameError(BaseOverhaveSynchronizerException):
    """Exception for situation without feature info name."""


class NullableInfoScenariosError(BaseOverhaveSynchronizerException):
    """Exception for situation without feature info scenarios."""


class NullableInfoAuthorError(BaseOverhaveSynchronizerException):
    """Exception for situation without feature info author."""


class NullableInfoFeatureTypeError(BaseOverhaveSynchronizerException):
    """Exception for situation without feature info type."""


class FeatureInfoUserNotFoundError(BaseOverhaveSynchronizerException):
    """Exception for situation without specified user in database."""


class OverhaveSynchronizer(BaseFileExtractor, IOverhaveSynchronizer):
    """Class for synchronization between git and database."""

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        feature_storage: IFeatureStorage,
        feature_type_storage: IFeatureTypeStorage,
        scenario_storage: IScenarioStorage,
        draft_storage: IDraftStorage,
        tag_storage: IFeatureTagStorage,
        scenario_parser: ScenarioParser,
        feature_extractor: FeatureExtractor,
        system_user_storage: ISystemUserStorage,
        git_initializer: GitRepositoryInitializer,
    ):
        super().__init__(extenstion=file_settings.feature_suffix)
        self._file_settings = file_settings
        self._feature_storage = feature_storage
        self._feature_type_storage = feature_type_storage
        self._scenario_storage = scenario_storage
        self._draft_storage = draft_storage
        self._tag_storage = tag_storage
        self._scenario_parser = scenario_parser
        self._feature_extractor = feature_extractor
        self._system_user_storage = system_user_storage
        self._git_initializer = git_initializer

    @staticmethod
    def _update_feature_model_with_info(
        model: FeatureModel, info: FeatureInfo, file_ts: datetime, tags: List[TagModel]
    ) -> None:
        if info.name is None:
            raise NullableInfoNameError("Feature info has not got feature name!")
        model.name = info.name
        if info.last_edited_by is not None:
            model.last_edited_by = info.last_edited_by
        model.last_edited_at = file_ts
        if info.tasks is not None:
            model.task = info.tasks
        model.feature_tags = tags

    def _get_last_change_time(self, model: FeatureModel) -> datetime:
        draft_models = self._draft_storage.get_drafts_by_feature_id(model.id)
        if draft_models:
            logger.info("Feature has got drafts.")
            last_published_draft = draft_models[-1]
            if last_published_draft.published_at is not None:
                logger.info(
                    "Last version has been published at %s.",
                    last_published_draft.published_at.strftime("%d-%m-%Y %H:%M:%S"),
                )
                return last_published_draft.published_at
        logger.info("Feature hasn't got any published version.")
        return model.last_edited_at

    def _get_feature_tags(self, info: FeatureInfo) -> List[TagModel]:
        tags: List[TagModel] = []
        if info.tags is not None:
            if info.last_edited_by is None:
                raise NullableInfoLastEditedByError("last_edited_by value should not be None!")
            for tag in info.tags:
                tag_model = self._tag_storage.get_or_create_tag(value=tag, created_by=info.last_edited_by)
                tags.append(tag_model)
        return tags

    def _ensure_users_exist(self, info: FeatureInfo) -> None:
        for user in (x for x in {info.author, info.last_edited_by} if x):
            if self._system_user_storage.get_user_by_credits(login=user) is not None:
                continue
            raise FeatureInfoUserNotFoundError(f"Could not find user with login={user}!")

    def _update_db_feature(self, model: FeatureModel, info: FeatureInfo, file_ts: datetime) -> None:
        logger.info("Feature is gonna be updated...")
        if info.scenarios is None:
            raise NullableInfoScenariosError("Some troubles with parsing feature - could not get scenarios!")
        self._ensure_users_exist(info)
        feature_tags = self._get_feature_tags(info=info)
        self._update_feature_model_with_info(model=model, info=info, file_ts=file_ts, tags=feature_tags)
        scenario_model = self._scenario_storage.get_scenario_by_feature_id(model.id)
        self._feature_storage.update_feature(model)
        scenario_model.text = info.scenarios
        self._scenario_storage.update_scenario(model=scenario_model)
        logger.info("Feature has been updated successfully.")

    def _create_feature(self, file: Path, info: FeatureInfo) -> None:
        logger.info("Feature is gonna be created...")
        if info.name is None:
            raise NullableInfoNameError("Feature info has not got feature name!")
        if info.type is None:
            raise NullableInfoFeatureTypeError("Could not create feature without feature type!")
        if info.author is None:
            raise NullableInfoAuthorError("Could not create feature without author!")
        self._ensure_users_exist(info)
        feature_tags = self._get_feature_tags(info=info)
        feature_type = self._feature_type_storage.get_feature_type_by_name(info.type)
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
        feature_model.id = self._feature_storage.create_feature(feature_model)
        scenario_model = ScenarioModel(id=0, feature_id=feature_model.id, text=info.scenarios)
        self._scenario_storage.create_scenario(scenario_model)
        logger.info("Feature with ID=%s has been created successfully.", feature_model.id)

    def synchronize(self, create_db_features: bool = False, pull_repository: bool = False) -> None:  # noqa: C901
        if pull_repository:
            self._git_initializer.pull()
        logger.info("Start synchronization...")
        all_features = self._extract_recursively(self._file_settings.features_dir)
        for feature_file in all_features:
            logger.info("Synchronize feature from file %s...", feature_file.as_posix())
            feature_info = self._scenario_parser.parse(feature_file.read_text())
            logger.debug("Parsed feature info: %s", feature_info)
            if feature_info.id is None:
                if not create_db_features:
                    logger.warning("Feature doesn't have Overhave ID or ID format is incorrect. Skip.")
                    continue
                self._create_feature(file=feature_file, info=feature_info)
                continue
            logger.info("Feature has ID=%s", feature_info.id)
            feature_model = self._feature_storage.get_feature(feature_info.id)
            if feature_model is None:
                logger.warning("Feature doesn't exist in Overhave database.")
                continue  # TODO: unlink file and create MR with deletions at the end

            feature_file_ts = datetime.fromtimestamp(feature_file.stat().st_mtime, tz=pytz.UTC)
            if feature_model.last_edited_at is None:
                raise NullableLastEditedAtError("last_edited_at value should not be None!")
            if feature_model.last_edited_at == feature_file_ts and feature_model.released:
                logger.warning("Feature has been already synchronized.")
                continue

            last_change_time = self._get_last_change_time(model=feature_model)
            if last_change_time < feature_file_ts:
                self._update_db_feature(model=feature_model, info=feature_info, file_ts=feature_file_ts)
                continue
            if feature_model.released:
                logger.info("Feature is already actual. Skip.")
                continue
            logger.info(
                "Feature was changed soon (at %s), but not released. Skip.",
                last_change_time.strftime("%d-%m-%Y %H:%M:%S"),
            )
        logger.info("Synchronization completed.")
