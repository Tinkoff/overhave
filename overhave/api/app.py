import fastapi as fastapi

from overhave.api.views import (
    tags_item_handler,
    tags_list_handler,
    test_user_get_spec_handler,
    test_user_handler,
    test_user_put_spec_handler,
)


def _get_tags_router() -> fastapi.APIRouter:
    tags_router = fastapi.APIRouter()
    tags_router.add_api_route(
        "/item",
        tags_item_handler,
        methods=["GET"],
        summary="Get FeatureTag",
        description="Get FeatureTag by `value`",
    )
    tags_router.add_api_route(
        "/list",
        tags_list_handler,
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
        summary="Get TestUser",
        description="Get TestUserModel by `user_id` or `user_name`",
    )
    test_user_router.add_api_route(
        "/{user_id}/specification",
        test_user_get_spec_handler,
        methods=["GET"],
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


def create_overhave_api() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    app.include_router(_get_tags_router(), prefix="/feature/tags", tags=["feature_tags"])
    app.include_router(_get_testuser_router(), prefix="/test_user", tags=["test_users"])
    return app
