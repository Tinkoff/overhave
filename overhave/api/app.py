from typing import List

import fastapi as fastapi

from overhave.api.auth import AuthToken, get_authorized_user
from overhave.api.views import (
    docs,
    favicon,
    login_for_access_token,
    tags_item_handler,
    tags_list_handler,
    test_user_get_spec_handler,
    test_user_handler,
    test_user_put_spec_handler,
)
from overhave.storage import TagModel, TestUserModel, TestUserSpecification


def _get_tags_router() -> fastapi.APIRouter:
    tags_router = fastapi.APIRouter()
    tags_router.add_api_route(
        "/item",
        tags_item_handler,
        methods=["GET"],
        response_model=TagModel,
        summary="Get FeatureTag",
        description="Get FeatureTag by `value`",
    )
    tags_router.add_api_route(
        "/list",
        tags_list_handler,
        response_model=List[TagModel],
        methods=["GET"],
        summary="Get FeatureTags",
        description="Get FeatureTags list like `value`",
    )
    return tags_router


def _get_testuser_router() -> fastapi.APIRouter:
    test_user_router = fastapi.APIRouter()
    test_user_router.add_api_route(
        "/",
        test_user_handler,
        methods=["GET"],
        response_model=TestUserModel,
        summary="Get TestUser",
        description="Get TestUserModel by `user_id` or `user_name`",
    )
    test_user_router.add_api_route(
        "/{user_id}/specification",
        test_user_get_spec_handler,
        methods=["GET"],
        response_model=TestUserSpecification,
        summary="Get TestUser specification",
        description="Get TestUserModel.specification by `user_id`",
    )
    test_user_router.add_api_route(
        "/{user_id}/specification",
        test_user_put_spec_handler,
        methods=["PUT"],
        summary="Put TestUser specification",
        description="Update TestUser.specification by `user_id` and given payload",
    )
    return test_user_router


def _get_auth_router() -> fastapi.APIRouter:
    auth_router = fastapi.APIRouter()
    auth_router.add_api_route(
        "/token",
        login_for_access_token,
        methods=["POST"],
        response_model=AuthToken,
        summary="Get OAuth2 token",
        description="Get OAuth2 token by username and password",
        include_in_schema=False,
    )
    return auth_router


def create_overhave_api() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    auth_deps = [fastapi.Depends(get_authorized_user)]

    app.include_router(_get_tags_router(), dependencies=auth_deps, prefix="/feature/tags", tags=["feature_tags"])
    app.include_router(_get_testuser_router(), dependencies=auth_deps, prefix="/test_user", tags=["test_users"])

    app.include_router(_get_auth_router())
    app.add_api_route("/", docs, methods=["GET"], include_in_schema=False)
    app.add_api_route("/favicon.ico", favicon, methods=["GET"], include_in_schema=False)
    return app
