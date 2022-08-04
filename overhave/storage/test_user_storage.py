import abc
from typing import List, Optional, cast

from overhave import db
from overhave.storage import FeatureTypeName, FeatureTypeStorage, TestUserModel, TestUserSpecification


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
    def get_test_user_by_id(user_id: int) -> Optional[TestUserModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_test_user_by_name(name: str) -> Optional[TestUserModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_test_users(feature_type_id: int, allow_update: bool) -> List[TestUserModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_test_user(
        name: str, specification: TestUserSpecification, created_by: str, feature_type: FeatureTypeName
    ) -> TestUserModel:
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
    def get_test_user_by_id(user_id: int) -> Optional[TestUserModel]:
        with db.create_session() as session:
            user: Optional[db.TestUser] = session.query(db.TestUser).get(user_id)
            if user is not None:
                return cast(TestUserModel, TestUserModel.from_orm(user))
            return None

    @staticmethod
    def get_test_user_by_name(name: str) -> Optional[TestUserModel]:
        with db.create_session() as session:
            user: Optional[db.TestUser] = session.query(db.TestUser).filter(db.TestUser.name == name).one_or_none()
            if user is not None:
                return cast(TestUserModel, TestUserModel.from_orm(user))
            return None

    @staticmethod
    def get_test_users(feature_type_id: int, allow_update: bool) -> List[TestUserModel]:
        with db.create_session() as session:
            db_users: List[db.TestUser] = (
                session.query(db.TestUser)
                .filter(db.TestUser.feature_type_id == feature_type_id, db.TestUser.allow_update == allow_update)
                .all()
            )
            return [cast(TestUserModel, TestUserModel.from_orm(user)) for user in db_users]

    @staticmethod
    def create_test_user(
        name: str, specification: TestUserSpecification, created_by: str, feature_type: FeatureTypeName
    ) -> TestUserModel:
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
            return cast(TestUserModel, TestUserModel.from_orm(test_user))

    @staticmethod
    def update_test_user_specification(user_id: int, specification: TestUserSpecification) -> None:
        with db.create_session() as session:
            test_user = session.query(db.TestUser).get(user_id)
            if test_user is None:
                raise TestUserDoesNotExistError(f"Test user with id {user_id} does not exist!")
            if not test_user.allow_update:
                raise TestUserUpdatingNotAllowedError(f"Test user updating with id {user_id} not allowed!")
            test_user.specification = specification

    @staticmethod
    def delete_test_user(user_id: int) -> None:
        with db.create_session() as session:
            user: Optional[db.TestUser] = session.query(db.TestUser).get(user_id)
            if user is None:
                raise TestUserDoesNotExistError(f"Test user with id {user_id} does not exist!")
            session.delete(user)
