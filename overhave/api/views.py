import logging

import fastapi

from overhave.api.deps import get_test_user_storage
from overhave.entities.converters import TestUserModel
from overhave.storage.test_user_storage import TestUserStorage

logger = logging.getLogger(__name__)


def get_test_user(
    user_id: int, test_user_storage: TestUserStorage = fastapi.Depends(get_test_user_storage)
) -> TestUserModel:
    logger.info("Getting %s with user_id=%s...", TestUserModel.__name__, user_id)
    test_user = test_user_storage.get_test_user_by_id(user_id)
    if test_user is None:
        raise fastapi.HTTPException(status_code=404, detail=f"User with id={user_id} does not exist")
    return test_user
