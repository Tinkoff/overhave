import abc
from typing import Optional, cast

from overhave import db
from overhave.db import create_session
from overhave.entities.converters import TestUserModel
from overhave.storage import FeatureTypeStorage


class BaseTestUserStorageException(Exception):
    """Base exception for :class:`FeatureStorage`."""


class TestUserDoesNotExistError(BaseTestUserStorageException):
    """Error for situation when feature not found."""


class ITestUserStorage(abc.ABC):
    """Abstract class for Test User storage."""

    @staticmethod
    @abc.abstractmethod
    def get_test_user_by_name(name: str) -> TestUserModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_test_user(name: str, specification: dict[str, str], created_by: str, feature_type: str) -> int:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_test_user_specification(user_id: int, specification: dict[str, str]) -> None:
        pass


class TestUserStorage(ITestUserStorage):
    """Class for Test User storage."""

    @staticmethod
    def get_test_user_by_name(name: str) -> TestUserModel:
        with create_session() as session:
            user: Optional[db.TestUser] = session.query(db.TestUser).filter(db.TestUser.name == name).one_or_none()
            if user is not None:
                return cast(TestUserModel, TestUserModel.from_orm(user))
            raise TestUserDoesNotExistError(f"Not found test user with name {name}!")

    @staticmethod
    def create_test_user(name: str, specification: dict[str, str], created_by: str, feature_type: str) -> int:
        feature_type = FeatureTypeStorage.get_feature_type_by_name(name=feature_type)
        with db.create_session() as session:
            test_user = db.TestUser(  # type: ignore
                name=name,
                specification=specification,
                feature_type_id=feature_type.id,
                created_by=created_by,
            )
            session.add(test_user)
            session.flush()
            return cast(int, test_user.id)

    @staticmethod
    def update_test_user_specification(user_id: int, specification: dict[str, str]) -> None:
        with db.create_session() as session:
            test_user = session.query(db.TestUser).get(user_id)
            if test_user is None:
                raise TestUserDoesNotExistError(f"Test user with id {user_id} does not exist!")
            test_user.specification = specification
            session.flush()
