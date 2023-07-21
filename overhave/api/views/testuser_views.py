import logging
from http import HTTPStatus

import fastapi

from overhave import db
from overhave.api.deps import get_feature_type_storage, get_test_user_storage
from overhave.storage import (
    FeatureTypeName,
    FeatureTypeNotExistsError,
    IFeatureTypeStorage,
    ITestUserStorage,
    TestUserDoesNotExistError,
    TestUserModel,
    TestUserSpecification,
    TestUserUpdatingNotAllowedError,
)

logger = logging.getLogger(__name__)


def _get_testuser_by_id_handler(user_id: int, test_user_storage: ITestUserStorage) -> TestUserModel:
    logger.info("Getting %s with user_id=%s...", TestUserModel.__name__, user_id)
    test_user = test_user_storage.get_testuser_model_by_id(user_id)
    if test_user is None:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with id={user_id} does not exist!"
        )
    return test_user


def _get_testuser_by_key_handler(user_key: str, test_user_storage: ITestUserStorage) -> TestUserModel:
    logger.info("Getting %s with user_key='%s'...", TestUserModel.__name__, user_key)
    test_user = test_user_storage.get_testuser_model_by_key(user_key)
    if test_user is None:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with key='{user_key}' does not exist!"
        )
    return test_user


def get_testuser_handler(
    user_id: int | None = None,
    user_key: str | None = None,
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> TestUserModel:
    if user_id is not None:
        return _get_testuser_by_id_handler(user_id=user_id, test_user_storage=test_user_storage)
    if user_key is not None:
        return _get_testuser_by_key_handler(user_key=user_key, test_user_storage=test_user_storage)
    raise fastapi.HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="'user_id' or 'user_key' query parameter should be set!"
    )


def delete_testuser_handler(
    user_id: int,
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> None:
    try:
        test_user_storage.delete_test_user(user_id)
    except TestUserDoesNotExistError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with id={user_id} does not exist!"
        )


def testuser_list_handler(
    feature_type: FeatureTypeName,
    allow_update: bool,
    feature_type_storage: IFeatureTypeStorage = fastapi.Depends(get_feature_type_storage),
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> list[TestUserModel]:
    logger.info(
        "Getting %s list with feature_type=%s and allow_update=%s ...",
        TestUserModel.__name__,
        feature_type,
        allow_update,
    )
    try:
        with db.create_session() as session:
            db_feature_type = feature_type_storage.feature_type_by_name(session=session, name=feature_type)
            return test_user_storage.get_test_users_by_feature_type_name(
                session=session, feature_type_id=db_feature_type.id, allow_update=allow_update
            )
    except FeatureTypeNotExistsError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"FeatureType with name='{feature_type}' does not exist!"
        )


def testuser_get_spec_handler(
    user_id: int, test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage)
) -> TestUserSpecification:
    test_user = _get_testuser_by_id_handler(user_id=user_id, test_user_storage=test_user_storage)
    return test_user.specification


def testuser_put_spec_handler(
    user_id: int,
    specification: dict[str, str | None],
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> None:
    logger.info("Updating %s for user_id=%s...", TestUserSpecification.__name__, user_id)
    try:
        test_user_storage.update_test_user_specification(
            user_id=user_id, specification=TestUserSpecification(specification)
        )
    except TestUserDoesNotExistError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with id={user_id} does not exist!"
        )
    except TestUserUpdatingNotAllowedError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User's updating with id={user_id} not allowed!"
        )
    logger.info("%s for user_id=%s was successfully updated", TestUserSpecification.__name__, user_id)
