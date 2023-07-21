import abc
from functools import cached_property

import sqlalchemy.orm as so

from overhave import db
from overhave.storage.converters import FeatureTypeModel, FeatureTypeName


class BaseFeatureTypeStorageException(Exception):
    """Base exception for :class:`FeatureTypeStorage`."""


class FeatureTypeNotExistsError(BaseFeatureTypeStorageException):
    """Exception for situation without specified feature type."""


class IFeatureTypeStorage(abc.ABC):
    """Abstract class for feature type storage."""

    @abc.abstractmethod
    @cached_property
    def default_feature_type_name(self) -> FeatureTypeName:
        pass

    @staticmethod
    @abc.abstractmethod
    def feature_type_by_name(session: so.Session, name: FeatureTypeName) -> db.FeatureType:
        pass

    @abc.abstractmethod
    @cached_property
    def all_feature_types(self) -> list[FeatureTypeModel]:
        pass


class FeatureTypeStorage(IFeatureTypeStorage):
    """Class for feature type storage."""

    @cached_property
    def default_feature_type_name(self) -> FeatureTypeName:
        with db.create_session() as session:
            row_entities: tuple[FeatureTypeName] | None = (
                session.query(db.FeatureType)
                .with_entities(db.FeatureType.name)
                .order_by(db.FeatureType.id.asc())
                .first()
            )
            if row_entities is None:
                raise FeatureTypeNotExistsError("No one feature type exists in db.FeatureType table!")
            return row_entities[0]

    @staticmethod
    def feature_type_by_name(session: so.Session, name: FeatureTypeName) -> db.FeatureType:
        feature_type = session.query(db.FeatureType).filter(db.FeatureType.name == name).one_or_none()
        if feature_type is None:
            raise FeatureTypeNotExistsError(f"Could not find feature type with name='{name}'!")
        return feature_type

    @cached_property
    def all_feature_types(self) -> list[FeatureTypeModel]:
        with db.create_session() as session:
            db_feature_types = session.query(db.FeatureType).all()
            return [FeatureTypeModel.model_validate(x) for x in db_feature_types]
