import abc
from typing import cast

import sqlalchemy.orm as so

from overhave import db


class IFeatureTagsStorage(abc.ABC):
    """ Abstract class for feature tags storage. """

    @staticmethod
    @abc.abstractmethod
    def create_tag(session: so.Session, value: str, created_by: str) -> int:
        pass


class FeatureTagsStorage(IFeatureTagsStorage):
    """ Class for feature tags storage. """

    @staticmethod
    def create_tag(session: so.Session, value: str, created_by: str) -> int:
        tag = db.Tags(value=value, created_by=created_by)
        session.add(tag)
        session.flush()
        return cast(int, tag.id)
