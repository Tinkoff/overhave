import abc

import sqlalchemy as sa
import sqlalchemy.orm as so
from pydantic import SecretStr

from overhave import db
from overhave.storage.converters import SystemUserModel


class ISystemUserStorage(abc.ABC):
    """Abstract class for system user storage."""

    @staticmethod
    @abc.abstractmethod
    def get_user(user_id: int) -> SystemUserModel | None:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_user(login: str, password: SecretStr | None = None, role: db.Role = db.Role.user) -> SystemUserModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_user_by_credits(
        session: so.Session, login: str, password: SecretStr | None = None
    ) -> SystemUserModel | None:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_user_role(session: so.Session, user_id: int, role: db.Role) -> None:
        pass


class SystemUserStorage(ISystemUserStorage):
    """Class for system user storage."""

    @staticmethod
    def get_user(user_id: int) -> SystemUserModel | None:
        with db.create_session() as session:
            db_user = session.get(db.UserRole, user_id)
            if db_user is not None:
                return SystemUserModel.from_orm(db_user)
            return None

    @staticmethod
    def create_user(login: str, password: SecretStr | None = None, role: db.Role = db.Role.user) -> SystemUserModel:
        with db.create_session() as session:
            db_password = None
            if password is not None:
                db_password = password.get_secret_value()
            db_user = db.UserRole(login=login, password=db_password, role=role)
            session.add(db_user)
            session.flush()
            return SystemUserModel.from_orm(db_user)

    @staticmethod
    def get_user_by_credits(
        session: so.Session, login: str, password: SecretStr | None = None
    ) -> SystemUserModel | None:
        query = session.query(db.UserRole).filter(db.UserRole.login == login)
        if password is not None:
            query = query.filter(db.UserRole.password == password.get_secret_value())
        db_user = query.one_or_none()
        if db_user is not None:
            return SystemUserModel.from_orm(db_user)
        return None

    @staticmethod
    def update_user_role(session: so.Session, user_id: int, role: db.Role) -> None:
        session.execute(sa.update(db.UserRole).where(db.UserRole.id == user_id).values(role=role))
