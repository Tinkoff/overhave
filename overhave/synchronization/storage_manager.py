import logging
from datetime import datetime
from typing import List, Optional

from overhave.scenario import StrictFeatureInfo
from overhave.storage import (
    FeatureModel,
    FeatureTypeModel,
    FeatureTypeName,
    IDraftStorage,
    IFeatureStorage,
    IFeatureTagStorage,
    IFeatureTypeStorage,
    IScenarioStorage,
    ISystemUserStorage,
    ScenarioModel,
    TagModel,
)
from overhave.utils import ANY_INT

logger = logging.getLogger(__name__)


class BaseSynchronizerStorageMixinException(Exception):
    """Base exception for :class:`SynchronizerStorageManager`."""


class FeatureInfoUserNotFoundError(BaseSynchronizerStorageMixinException):
    """Exception for situation without specified user in database."""


class SynchronizerStorageManager:
    """Class for storages management while synchronizing features."""

    def __init__(
        self,
        feature_storage: IFeatureStorage,
        feature_type_storage: IFeatureTypeStorage,
        scenario_storage: IScenarioStorage,
        tag_storage: IFeatureTagStorage,
        draft_storage: IDraftStorage,
        system_user_storage: ISystemUserStorage,
    ) -> None:
        self._feature_storage = feature_storage
        self._feature_type_storage = feature_type_storage
        self._scenario_storage = scenario_storage
        self._tag_storage = tag_storage
        self._draft_storage = draft_storage
        self._system_user_storage = system_user_storage

    def get_feature(self, feature_id: int) -> Optional[FeatureModel]:
        return self._feature_storage.get_feature(feature_id)

    def get_last_change_time(self, model: FeatureModel) -> datetime:
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

    def get_feature_tags(self, info: StrictFeatureInfo) -> List[TagModel]:
        tags: List[TagModel] = []
        if info.tags is not None:
            for tag in info.tags:
                tag_model = self._tag_storage.get_or_create_tag(value=tag, created_by=info.last_edited_by)
                tags.append(tag_model)
        return tags

    def get_feature_type(self, feature_type: FeatureTypeName) -> FeatureTypeModel:
        return self._feature_type_storage.get_feature_type_by_name(feature_type)

    def ensure_users_exist(self, info: StrictFeatureInfo) -> None:
        for user in (x for x in {info.author, info.last_edited_by} if x):
            if self._system_user_storage.get_user_by_credits(login=user) is not None:
                continue
            raise FeatureInfoUserNotFoundError(f"Could not find user with login={user}!")

    def update_db_feature(self, model: FeatureModel, scenario: str) -> None:
        scenario_model = self._scenario_storage.get_scenario_by_feature_id(model.id)
        self._feature_storage.update_feature(model)
        scenario_model.text = scenario
        self._scenario_storage.update_scenario(model=scenario_model)

    def create_db_feature(self, model: FeatureModel, scenario: str) -> None:
        model.id = self._feature_storage.create_feature(model)
        scenario_model = ScenarioModel(id=ANY_INT, feature_id=model.id, text=scenario)
        self._scenario_storage.create_scenario(scenario_model)
