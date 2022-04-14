import abc
from typing import Optional, cast

from pydantic import SecretStr

from overhave import db
from overhave.storage.converters import SystemUserModel


class BaseSystemStorageException(Exception):
    """Base exception for :class:`SystemUserStorage`."""


class SystemUserNotFoundError(Exception):
    """Error for situation without user with given id."""


class ISystemUserStorage(abc.ABC):
    """Abstract class for system user storage."""

    @staticmethod
    @abc.abstractmethod
    def get_user(user_id: int) -> Optional[SystemUserModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_user(login: str, password: Optional[SecretStr] = None, role: db.Role = db.Role.user) -> SystemUserModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_user_by_credits(login: str, password: Optional[SecretStr] = None) -> Optional[SystemUserModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_user_role(user_model: SystemUserModel) -> None:
        pass


class SystemUserStorage(ISystemUserStorage):
    """Class for system user storage."""

    @staticmethod
    def get_user(user_id: int) -> Optional[SystemUserModel]:
        with db.create_session() as session:
            db_user = session.query(db.UserRole).get(user_id)
            if db_user is not None:
                return cast(SystemUserModel, SystemUserModel.from_orm(db_user))
            return None

    @staticmethod
    def create_user(login: str, password: Optional[SecretStr] = None, role: db.Role = db.Role.user) -> SystemUserModel:
        with db.create_session() as session:
            db_password = None
            if password is not None:
                db_password = password.get_secret_value()
            db_user = db.UserRole(login=login, password=db_password, role=role)
            session.add(db_user)
            session.flush()
            return cast(SystemUserModel, SystemUserModel.from_orm(db_user))

    @staticmethod
    def get_user_by_credits(login: str, password: Optional[SecretStr] = None) -> Optional[SystemUserModel]:
        with db.create_session() as session:
            query = session.query(db.UserRole).filter(db.UserRole.login == login)
            if password is not None:
                query = query.filter(db.UserRole.password == password.get_secret_value())
            db_user = query.one_or_none()
            if db_user is not None:
                return cast(SystemUserModel, SystemUserModel.from_orm(db_user))
            return None

    @staticmethod
    def update_user_role(user_model: SystemUserModel) -> None:
        with db.create_session() as session:
            db_user = session.query(db.UserRole).get(user_model.id)
            if db_user is None:
                raise SystemUserNotFoundError(f"User with id {user_model.id} was not found!")
            db_user.role = user_model.role
