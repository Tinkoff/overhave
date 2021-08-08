import abc
from typing import cast

import sqlalchemy.orm as so

from overhave import db
from overhave.entities import FeatureModel


class BaseFeatureStorageException(Exception):
    """ Base exception for :class:`FeatureStorage`. """


class FeatureNotExistsError(BaseFeatureStorageException):
    """ Error for situation when feature not found. """


class IFeatureStorage(abc.ABC):
    """ Abstract class for feature storage. """

    @staticmethod
    @abc.abstractmethod
    def get_feature(feature_id: int) -> FeatureModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_feature(session: so.Session, model: FeatureModel) -> None:
        pass


class FeatureStorage(IFeatureStorage):
    """ Class for feature storage. """

    @staticmethod
    def get_feature(feature_id: int) -> FeatureModel:
        with db.create_session() as session:
            feature: db.Feature = session.query(db.Feature).filter(db.Feature.id == feature_id).one()
            return cast(FeatureModel, FeatureModel.from_orm(feature))

    @staticmethod
    def create_feature(session: so.Session, model: FeatureModel) -> None:
        feature = db.Feature(
            name=model.name,
            author=model.author,
            type_id=model.feature_type.id,
            file_path=model.file_path,
            task=model.task,
        )
        session.add(feature)

    @staticmethod
    def update_feature(session: so.Session, model: FeatureModel) -> None:
        feature: db.Feature = session.query(db.Feature).get(model.id)
        if feature is None:
            raise FeatureNotExistsError(f"Feature with id {model.id} does not exist!")
        feature.name = model.name
        feature.type_id = model.feature_type.id
        feature.file_path = model.file_path
        feature.task = model.task
        feature.last_edited_by = model.last_edited_by
        feature.released = True
