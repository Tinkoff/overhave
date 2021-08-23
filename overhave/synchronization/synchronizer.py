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
        if info.last_edited_by is not None:
            model.last_edited_at = file_ts
        if info.tasks is not None:
            model.task = info.tasks
        model.feature_tags = tags

    def synchronize(self) -> None:  # noqa: C901
        logger.info("Start synchronization...")
        all_features = self._extract_recursively(self._file_settings.features_dir)
        for feature_file in all_features:
            logger.info("Synchronize feature from file %s...", feature_file.as_posix())
            feature_info = self._scenario_parser.parse(feature_file.read_text())
            if feature_info.id is None:
                logger.warning("Feature doesn't have Overhave ID or ID format is incorrect - skip.")
                continue
            if feature_info.scenarios is None:
                raise NullableInfoScenariosError("Some troubles with parsing feature - could not get scenarios!")
            feature_model = self._feature_storage.get_feature(feature_info.id)
            if feature_model is None:
                logger.warning("Feature doesn't exist in Overhave database, so drop it.")
                feature_file.unlink()
                continue
            feature_file_ts = datetime.fromtimestamp(feature_file.stat().st_mtime)
            if feature_model.last_edited_at is None:
                raise NullableLastEditedAtError("last_edited_at value should not be None!")
            comparison_time = feature_model.last_edited_at
            if comparison_time == feature_file_ts and feature_model.released:
                logger.warning("Feature has been already synchronized.")
                continue
            draft_models = self._draft_storage.get_drafts_by_feature_id(feature_model.id)
            if draft_models:
                logger.info("Feature has got drafts.")
                last_published_draft = draft_models[-1]
                if last_published_draft.published_at is not None:
                    logger.info(
                        "Last version has been published at %s.", last_published_draft.strftime("%d-%m-%Y %H:%M:%S")
                    )
                    comparison_time = last_published_draft.published_at
                else:
                    logger.info("Feature hasn't got any published version.")
            else:
                logger.info("Feature hasn't got any published version.")

            if comparison_time < feature_file_ts:
                logger.info("Feature is gonna be updated...")
                feature_tags: List[TagModel] = []
                if feature_info.tags is not None:
                    if feature_info.last_edited_by is None:
                        logger.warning("Feature doesn't have last_edited_by info!")
                    else:
                        for tag in feature_info.tags:
                            tag_model = self._tag_storage.get_or_create_tag(
                                value=tag, created_by=feature_info.last_edited_by
                            )
                            feature_tags.append(tag_model)
                self._update_feature_model_with_info(
                    model=feature_model, info=feature_info, file_ts=feature_file_ts, tags=feature_tags
                )
                scenario_model = self._scenario_storage.get_scenario_by_feature_id(feature_model.id)
                self._feature_storage.update_feature(feature_model)
                scenario_model.text = feature_info.scenarios
                self._scenario_storage.update_scenario(model=scenario_model)
                logger.info("Feature has been updated successfully.")
                continue
            if feature_model.released:
                logger.info("Feature is already actual. Skip.")
                continue
            logger.info(
                "Feature was changed soon (at %s), but not released. Skip.",
                comparison_time.strftime("%d-%m-%Y %H:%M:%S"),
            )
        logger.info("Synchronization completed.")
