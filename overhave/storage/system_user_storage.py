import abc

import sqlalchemy.orm as so
from pydantic import SecretStr

from overhave import db
from overhave.storage.converters import SystemUserModel


class ISystemUserStorage(abc.ABC):
    """Abstract class for system user storage."""

    @staticmethod
    @abc.abstractmethod
    def get_user_model(user_id: int) -> SystemUserModel | None:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_user(
        session: so.Session, login: str, password: SecretStr | None = None, role: db.Role = db.Role.user
    ) -> db.UserRole:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_user_by_credits(session: so.Session, login: str, password: SecretStr | None = None) -> db.UserRole | None:
        pass


class SystemUserStorage(ISystemUserStorage):
    """Class for system user storage."""

    @staticmethod
    def get_user_model(user_id: int) -> SystemUserModel | None:
        with db.create_session() as session:
            db_user = session.get(db.UserRole, user_id)
            if db_user is not None:
                return SystemUserModel.model_validate(db_user)
            return None

    @staticmethod
    def create_user(
        session: so.Session, login: str, password: SecretStr | None = None, role: db.Role = db.Role.user
    ) -> db.UserRole:
        db_password = None
        if password is not None:
            db_password = password.get_secret_value()
        db_user = db.UserRole(login=login, password=db_password, role=role)
        session.add(db_user)
        session.flush()
        return db_user

    @staticmethod
    def get_user_by_credits(session: so.Session, login: str, password: SecretStr | None = None) -> db.UserRole | None:
        query = session.query(db.UserRole).filter(db.UserRole.login == login)
        if password is not None:
            query = query.filter(db.UserRole.password == password.get_secret_value())
        return query.one_or_none()
