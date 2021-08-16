import abc
from typing import Optional, cast

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
    def get_feature(feature_id: int) -> Optional[FeatureModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_feature(model: FeatureModel) -> int:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_feature(model: FeatureModel) -> None:
        pass


class FeatureStorage(IFeatureStorage):
    """ Class for feature storage. """

    @staticmethod
    def get_feature(feature_id: int) -> Optional[FeatureModel]:
        with db.create_session() as session:
            feature: Optional[db.Feature] = session.query(db.Feature).get(feature_id)
            if feature is not None:
                return cast(FeatureModel, FeatureModel.from_orm(feature))
            return None

    @staticmethod
    def create_feature(model: FeatureModel) -> int:
        with db.create_session() as session:
            feature = db.Feature(
                name=model.name,
                author=model.author,
                type_id=model.feature_type.id,
                file_path=model.file_path,
                task=model.task,
            )
            session.add(feature)
            session.flush()
            return cast(int, feature.id)

    @staticmethod
    def update_feature(model: FeatureModel) -> None:
        with db.create_session() as session:
            feature: db.Feature = session.query(db.Feature).get(model.id)
            if feature is None:
                raise FeatureNotExistsError(f"Feature with id {model.id} does not exist!")
            feature.name = model.name
            feature.file_path = model.file_path
            feature.task = model.task
            feature.last_edited_by = model.last_edited_by
            feature.released = True
