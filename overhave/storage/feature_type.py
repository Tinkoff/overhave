import abc
from typing import cast

from overhave import db
from overhave.entities.converters import FeatureTypeModel


class IFeatureTypeStorage(abc.ABC):
    """ Abstract class for feature type storage. """

    @abc.abstractmethod
    def get_default_feature_type(self) -> FeatureTypeModel:
        pass


class FeatureTypeStorage(IFeatureTypeStorage):
    """ Class for feature type storage. """

    def get_default_feature_type(self) -> FeatureTypeModel:
        with db.create_session() as session:
            feature_type: db.FeatureType = session.query(db.FeatureType).order_by(db.FeatureType.id.asc()).first()
            return cast(FeatureTypeModel, FeatureTypeModel.from_orm(feature_type))
