import logging
from datetime import datetime

import sqlalchemy.orm as so

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

    def get_feature(self, feature_id: int) -> FeatureModel | None:
        return self._feature_storage.get_feature_model(feature_id)

    def get_last_change_time(self, model: FeatureModel) -> datetime:
        last_draft_published_at = self._draft_storage.get_last_published_at_for_feature(model.id)
        if last_draft_published_at is not None:
            logger.info(
                "Last version has been published at %s.",
                last_draft_published_at.strftime("%d-%m-%Y %H:%M:%S"),
            )
            return last_draft_published_at
        logger.info("Feature hasn't got any published version.")
        return model.last_edited_at

    def get_feature_tags(self, session: so.Session, info: StrictFeatureInfo) -> list[TagModel]:
        db_tags = [
            self._tag_storage.get_or_create_tag(session=session, value=tag, created_by=info.last_edited_by)
            for tag in info.tags
        ]
        session.flush()
        return [TagModel.model_validate(x) for x in db_tags]

    def feature_type_by_name(self, session: so.Session, feature_type: FeatureTypeName) -> FeatureTypeModel:
        db_feature_type = self._feature_type_storage.feature_type_by_name(session=session, name=feature_type)
        return FeatureTypeModel.model_validate(db_feature_type)

    def ensure_users_exist(self, session: so.Session, info: StrictFeatureInfo) -> None:
        for user in {info.author, info.last_edited_by}:
            if self._system_user_storage.get_user_by_credits(session=session, login=user):
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
