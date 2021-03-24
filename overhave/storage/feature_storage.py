import abc
from typing import cast

from overhave import db
from overhave.entities import FeatureModel


class IFeatureStorage(abc.ABC):
    """ Abstract class for feature storage. """

    @abc.abstractmethod
    def get_feature(self, feature_id: int) -> FeatureModel:
        pass


class FeatureStorage(IFeatureStorage):
    """ Class for feature storage. """

    def get_feature(self, feature_id: int) -> FeatureModel:
        with db.create_session() as session:
            scenario: db.Feature = session.query(db.Feature).filter(db.Feature.id == feature_id).one()
            return cast(FeatureModel, FeatureModel.from_orm(scenario))
