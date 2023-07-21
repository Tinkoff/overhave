import abc

import sqlalchemy as sa
import sqlalchemy.orm as so

from overhave import db
from overhave.storage import TestUserModel, TestUserSpecification
from overhave.utils import get_current_time


class BaseTestUserStorageException(Exception):
    """Base exception for :class:`FeatureStorage`."""


class TestUserDoesNotExistError(BaseTestUserStorageException):
    """Error for situation when test user not found."""

    __test__ = False


class TestUserUpdatingNotAllowedError(BaseTestUserStorageException):
    """Error for situation when test user has allow_update=False."""

    __test__ = False


class ITestUserStorage(abc.ABC):
    """Abstract class for Test User storage."""

    @staticmethod
    @abc.abstractmethod
    def get_testuser_model_by_id(user_id: int) -> TestUserModel | None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_testuser_model_by_key(key: str) -> TestUserModel | None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_test_users_by_feature_type_name(
        session: so.Session, feature_type_id: int, allow_update: bool
    ) -> list[TestUserModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_test_user_specification(user_id: int, specification: TestUserSpecification) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def delete_test_user(user_id: int) -> None:
        pass


class TestUserStorage(ITestUserStorage):
    """Class for Test User storage."""

    @staticmethod
    def get_testuser_model_by_id(user_id: int) -> TestUserModel | None:
        with db.create_session() as session:
            user = session.get(db.TestUser, user_id)
            if user is not None:
                return TestUserModel.model_validate(user)
            return None

    @staticmethod
    def get_testuser_model_by_key(key: str) -> TestUserModel | None:
        with db.create_session() as session:
            user: db.TestUser | None = session.query(db.TestUser).filter(db.TestUser.key == key).one_or_none()
            if user is not None:
                return TestUserModel.model_validate(user)
            return None

    @staticmethod
    def get_test_users_by_feature_type_name(
        session: so.Session, feature_type_id: int, allow_update: bool
    ) -> list[TestUserModel]:
        db_users = (
            session.query(db.TestUser)
            .filter(db.TestUser.feature_type_id == feature_type_id, db.TestUser.allow_update.is_(allow_update))
            .all()
        )
        return [TestUserModel.model_validate(user) for user in db_users]

    @staticmethod
    def update_test_user_specification(user_id: int, specification: TestUserSpecification) -> None:
        with db.create_session() as session:
            test_user = session.get(db.TestUser, user_id)
            if test_user is None:
                raise TestUserDoesNotExistError(f"Test user with id {user_id} does not exist!")
            if not test_user.allow_update:
                raise TestUserUpdatingNotAllowedError(f"Test user updating with id {user_id} not allowed!")
            session.execute(
                sa.update(db.TestUser)
                .where(db.TestUser.id == test_user.id)
                .values(specification=specification, changed_at=get_current_time())
            )

    @staticmethod
    def delete_test_user(user_id: int) -> None:
        with db.create_session() as session:
            user = session.get(db.TestUser, user_id)
            if user is None:
                raise TestUserDoesNotExistError(f"Test user with id {user_id} does not exist!")
            session.delete(user)
