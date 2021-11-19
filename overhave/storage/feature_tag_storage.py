import abc
from typing import Optional, cast

from overhave import db
from overhave.entities import TagModel


class IFeatureTagStorage(abc.ABC):
    """Abstract class for feature tags storage."""

    @staticmethod
    @abc.abstractmethod
    def get_or_create_tag(value: str, created_by: str) -> TagModel:
        pass


class FeatureTagStorage(IFeatureTagStorage):
    """Class for feature tags storage."""

    @staticmethod
    def get_or_create_tag(value: str, created_by: str) -> TagModel:
        with db.create_session() as session:
            tag: Optional[db.Tags] = session.query(db.Tags).filter(db.Tags.value == value).one_or_none()
            if tag is None:
                tag = db.Tags(value=value, created_by=created_by)
                session.add(tag)
                session.flush()
            return cast(TagModel, TagModel.from_orm(tag))
