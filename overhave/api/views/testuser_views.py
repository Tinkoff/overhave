import logging
from http import HTTPStatus
from typing import List, Optional

import fastapi

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


def _get_test_user_by_id_handler(user_id: int, test_user_storage: ITestUserStorage) -> TestUserModel:
    logger.info("Getting %s with user_id=%s...", TestUserModel.__name__, user_id)
    test_user = test_user_storage.get_test_user_by_id(user_id)
    if test_user is None:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with id={user_id} does not exist!"
        )
    return test_user


def _get_test_user_by_name_handler(user_name: str, test_user_storage: ITestUserStorage) -> TestUserModel:
    logger.info("Getting %s with user_name='%s'...", TestUserModel.__name__, user_name)
    test_user = test_user_storage.get_test_user_by_name(user_name)
    if test_user is None:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with name='{user_name}' does not exist!"
        )
    return test_user


def get_test_user_handler(
    user_id: Optional[int] = None,
    user_name: Optional[str] = None,
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> TestUserModel:
    if user_id is not None:
        return _get_test_user_by_id_handler(user_id=user_id, test_user_storage=test_user_storage)
    if user_name is not None:
        return _get_test_user_by_name_handler(user_name=user_name, test_user_storage=test_user_storage)
    raise fastapi.HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="'user_id' or 'user_name' query parameter should be set!"
    )


def delete_test_user_handler(
    user_id: int,
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> None:
    try:
        test_user_storage.delete_test_user(user_id)
    except TestUserDoesNotExistError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with id={user_id} does not exist!"
        )


def test_user_list_handler(
    feature_type: FeatureTypeName,
    allow_update: bool,
    feature_type_storage: IFeatureTypeStorage = fastapi.Depends(get_feature_type_storage),
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> List[TestUserModel]:
    logger.info(
        "Getting %s list with feature_type=%s and allow_update=%s ...",
        TestUserModel.__name__,
        feature_type,
        allow_update,
    )
    try:
        feature_type_model = feature_type_storage.get_feature_type_by_name(feature_type)
        return test_user_storage.get_test_users(feature_type_id=feature_type_model.id, allow_update=allow_update)
    except FeatureTypeNotExistsError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"FeatureType with name='{feature_type}' does not exist!"
        )


def test_user_get_spec_handler(
    user_id: int, test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage)
) -> TestUserSpecification:
    test_user = _get_test_user_by_id_handler(user_id=user_id, test_user_storage=test_user_storage)
    return test_user.specification


def test_user_put_spec_handler(
    user_id: int,
    specification: TestUserSpecification,
    test_user_storage: ITestUserStorage = fastapi.Depends(get_test_user_storage),
) -> None:
    logger.info("Updating %s for user_id=%s...", TestUserSpecification.__name__, user_id)
    try:
        test_user_storage.update_test_user_specification(user_id=user_id, specification=specification)
    except TestUserDoesNotExistError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User with id={user_id} does not exist!"
        )
    except TestUserUpdatingNotAllowedError:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"User's updating with id={user_id} not allowed!"
        )
    logger.info("%s for user_id=%s was successfully updated", TestUserSpecification.__name__, user_id)
