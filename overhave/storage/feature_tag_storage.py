import abc

from overhave import db
from overhave.storage.converters import TagModel


class IFeatureTagStorage(abc.ABC):
    """Abstract class for feature tags storage."""

    @staticmethod
    @abc.abstractmethod
    def get_tag_by_value(value: str) -> TagModel | None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_tags_like_value(value: str) -> list[TagModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_or_create_tag(value: str, created_by: str) -> TagModel:
        pass


class FeatureTagStorage(IFeatureTagStorage):
    """Class for feature tags storage."""

    @staticmethod
    def get_tag_by_value(value: str) -> TagModel | None:
        with db.create_session() as session:
            tag = session.query(db.Tags).filter(db.Tags.value == value).one_or_none()
            if tag is not None:
                return TagModel.from_orm(tag)
            return None

    @staticmethod
    def get_tags_like_value(value: str) -> list[TagModel]:
        with db.create_session() as session:
            db_tags = session.query(db.Tags).filter(db.Tags.value.like(value)).all()
            return [TagModel.from_orm(tag) for tag in db_tags]

    @staticmethod
    def get_or_create_tag(value: str, created_by: str) -> TagModel:
        with db.create_session() as session:
            tag = session.query(db.Tags).filter(db.Tags.value == value).one_or_none()
            if tag is None:
                tag = db.Tags(value=value, created_by=created_by)
                session.add(tag)
                session.flush()
            return TagModel.from_orm(tag)
