import abc
import logging
from datetime import datetime
from typing import List

from overhave.entities import BaseFileExtractor, FeatureModel, OverhaveFileSettings, TagModel
from overhave.scenario import ScenarioParser
from overhave.scenario.parser import FeatureInfo
from overhave.storage import IDraftStorage, IFeatureStorage, IFeatureTagStorage, IScenarioStorage

logger = logging.getLogger(__name__)


class BaseOverhaveSynchronizerException(Exception):
    """ Base exception for :class:`OverhaveSynchronizer`. """


class NullableLastEditedAtError(BaseOverhaveSynchronizerException):
    """ Exception for nullable last_edited_at. """


class NullableLastEditedByError(BaseOverhaveSynchronizerException):
    """ Exception for nullable last_edited_at. """


class NullableInfoNameError(BaseOverhaveSynchronizerException):
    """ Exception for situation without feature info name. """


class NullableInfoScenariosError(BaseOverhaveSynchronizerException):
    """ Exception for situation without feature info scenarios. """


class IOverhaveSynchronizer(abc.ABC):
    """ Abstract class for synchronization between git and database. """

    @abc.abstractmethod
    def synchronize(self) -> None:
        pass


class OverhaveSynchronizer(BaseFileExtractor, IOverhaveSynchronizer):
    """ Class for synchronization between git and database. """

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        feature_storage: IFeatureStorage,
        scenario_storage: IScenarioStorage,
        draft_storage: IDraftStorage,
        tag_storage: IFeatureTagStorage,
        scenario_parser: ScenarioParser,
    ):
        super().__init__(extenstion=file_settings.feature_suffix)
        self._file_settings = file_settings
        self._feature_storage = feature_storage
        self._scenario_storage = scenario_storage
        self._draft_storage = draft_storage
        self._tag_storage = tag_storage
        self._scenario_parser = scenario_parser

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
                    "Last version has been published at %s.", last_published_draft.strftime("%d-%m-%Y %H:%M:%S")
                )
                return last_published_draft.published_at
        logger.info("Feature hasn't got any published version.")
        return model.last_edited_at

    def _get_feature_tags(self, info: FeatureInfo) -> List[TagModel]:
        tags: List[TagModel] = []
        if info.tags is not None:
            if info.last_edited_by is None:
                raise NullableLastEditedByError("last_edited_by value should not be None!")
            for tag in info.tags:
                tag_model = self._tag_storage.get_or_create_tag(value=tag, created_by=info.last_edited_by)
                tags.append(tag_model)
        return tags

    def _update_db_feature(self, model: FeatureModel, info: FeatureInfo, file_ts: datetime) -> None:
        logger.info("Feature is gonna be updated...")
        if info.scenarios is None:
            raise NullableInfoScenariosError("Some troubles with parsing feature - could not get scenarios!")
        feature_tags = self._get_feature_tags(info=info)
        self._update_feature_model_with_info(model=model, info=info, file_ts=file_ts, tags=feature_tags)
        scenario_model = self._scenario_storage.get_scenario_by_feature_id(model.id)
        self._feature_storage.update_feature(model)
        scenario_model.text = info.scenarios
        self._scenario_storage.update_scenario(model=scenario_model)
        logger.info("Feature has been updated successfully.")

    def synchronize(self) -> None:  # noqa: C901
        logger.info("Start synchronization...")
        all_features = self._extract_recursively(self._file_settings.features_dir)
        for feature_file in all_features:
            logger.info("Synchronize feature from file %s...", feature_file.as_posix())
            feature_info = self._scenario_parser.parse(feature_file.read_text())
            if feature_info.id is None:
                logger.warning("Feature doesn't have Overhave ID or ID format is incorrect - skip.")
                continue
            feature_model = self._feature_storage.get_feature(feature_info.id)
            if feature_model is None:
                logger.warning("Feature doesn't exist in Overhave database, so drop it.")
                feature_file.unlink()
                continue

            feature_file_ts = datetime.fromtimestamp(feature_file.stat().st_mtime)
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
