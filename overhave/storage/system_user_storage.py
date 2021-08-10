import abc
from typing import Optional, cast

from overhave import db
from overhave.entities import SystemUserModel


class ISystemUserStorage(abc.ABC):
    """ Abstract class for system user storage. """

    @staticmethod
    @abc.abstractmethod
    def create_user(login: str, password: Optional[str], role: db.Role) -> SystemUserModel:
        pass


class SystemUserStorage(ISystemUserStorage):
    """ Class for system user storage. """

    @staticmethod
    def create_user(login: str, password: Optional[str] = None, role: db.Role = db.Role.user) -> SystemUserModel:
        with db.create_session() as session:
            app_user = db.UserRole(login=login, password=password, role=role)
            session.add(app_user)
            session.flush()
            return cast(SystemUserModel, SystemUserModel.from_orm(app_user))
