import abc

import sqlalchemy.orm as so

from overhave import db


class ISystemUserGroupStorage(abc.ABC):
    """Abstract class for system user storage."""

    @staticmethod
    @abc.abstractmethod
    def has_any_group(session: so.Session, user_groups: list[str]) -> bool:
        pass


class SystemUserGroupStorage(ISystemUserGroupStorage):
    """Class for system user storage."""

    @staticmethod
    def has_any_group(session: so.Session, user_groups: list[str]) -> bool:
        return session.query(db.GroupRole).filter(db.GroupRole.group.in_(user_groups)).first() is not None
