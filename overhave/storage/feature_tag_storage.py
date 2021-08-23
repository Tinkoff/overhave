import abc
from typing import Optional, cast

import sqlalchemy.orm as so

from overhave import db


class IFeatureTagStorage(abc.ABC):
    """ Abstract class for feature tags storage. """

    @staticmethod
    @abc.abstractmethod
    def get_or_create_tag(session: so.Session, value: str, created_by: str) -> int:
        pass


class FeatureTagStorage(IFeatureTagStorage):
    """ Class for feature tags storage. """

    @staticmethod
    def get_or_create_tag(session: so.Session, value: str, created_by: str) -> int:
        tag: Optional[db.Tags] = session.query(db.Tags).filter(db.Tags.value == value).one_or_none()
        if tag is not None:
            return cast(int, tag.id)
        tag = db.Tags(value=value, created_by=created_by)
        session.add(tag)
        session.flush()
        return cast(int, tag.id)
