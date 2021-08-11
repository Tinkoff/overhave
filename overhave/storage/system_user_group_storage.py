import abc
from typing import List

from overhave import db


class ISystemUserGroupStorage(abc.ABC):
    """ Abstract class for system user storage. """

    @staticmethod
    @abc.abstractmethod
    def has_any_group(user_groups: List[str]) -> bool:
        pass


class SystemUserGroupStorage(ISystemUserGroupStorage):
    """ Class for system user storage. """

    @staticmethod
    def has_any_group(user_groups: List[str]) -> bool:
        with db.create_session() as session:
            return bool(session.query(db.GroupRole).filter(db.GroupRole.group.in_(user_groups)).all())
