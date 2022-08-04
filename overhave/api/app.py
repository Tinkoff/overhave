from typing import List

import fastapi

from overhave.api.auth import get_authorized_user
from overhave.api.views import (
    delete_test_user_handler,
    docs,
    emulation_run_list_handler,
    favicon,
    get_features_handler,
    get_test_run_handler,
    get_test_user_handler,
    login_for_access_token,
    run_tests_by_tag_handler,
    tags_item_handler,
    tags_list_handler,
    test_user_get_spec_handler,
    test_user_list_handler,
    test_user_put_spec_handler,
)
from overhave.storage import (
    AuthToken,
    EmulationRunModel,
    FeatureModel,
    TagModel,
    TestRunModel,
    TestUserModel,
    TestUserSpecification,
)


def _get_tags_router() -> fastapi.APIRouter:
    tags_router = fastapi.APIRouter()
    tags_router.add_api_route(
        "/item",
        tags_item_handler,
        methods=["GET"],
        response_model=TagModel,
        summary="Get FeatureTag",
        description="Get feature tag by `value`",
    )
    tags_router.add_api_route(
        "/list",
        tags_list_handler,
        response_model=List[TagModel],
        methods=["GET"],
        summary="Get FeatureTags",
        description="Get list of feature tags like `value`",
    )
    return tags_router


def _get_feature_router() -> fastapi.APIRouter:
    feature_router = fastapi.APIRouter()
    feature_router.add_api_route(
        "/",
        get_features_handler,
        methods=["GET"],
        response_model=List[FeatureModel],
        summary="Get list of Feature info",
        description="Get list of feature info by `tag_id` or `tag_value`",
    )
    return feature_router


def _get_testrun_router() -> fastapi.APIRouter:
    test_run_router = fastapi.APIRouter()
    test_run_router.add_api_route(
        "/",
        get_test_run_handler,
        methods=["GET"],
        response_model=TestRunModel,
        summary="Get test run by id",
        description="Get test run by `id`",
    )
    test_run_router.add_api_route(
        "/create/",
        run_tests_by_tag_handler,
        methods=["POST"],
        response_model=list[str],
        summary="Create TestRunTasks for Features by tag_value",
        description="Create TestRunTasks for Features by `tag_value`",
    )
    return test_run_router


def _get_testuser_router() -> fastapi.APIRouter:
    test_user_router = fastapi.APIRouter()

    test_user_router.add_api_route(
        "/",
        get_test_user_handler,
        methods=["GET"],
        response_model=TestUserModel,
        summary="Get TestUser",
        description="Get test user full info by `user_id` or `user_name`",
    )
    test_user_router.add_api_route(
        "/list",
        test_user_list_handler,
        methods=["GET"],
        response_model=List[TestUserModel],
        summary="Get list of TestUsers",
        description="Get list of test users with given `feature_type` and `allow_update`",
    )
    test_user_router.add_api_route(
        "/{user_id}/delete",
        delete_test_user_handler,
        methods=["DELETE"],
        summary="Delete TestUser",
        description="Delete test user by `user_id`",
    )
    test_user_router.add_api_route(
        "/{user_id}/specification",
        test_user_get_spec_handler,
        methods=["GET"],
        response_model=TestUserSpecification,
        summary="Get TestUser specification",
        description="Get test user specification by `user_id`",
    )
    test_user_router.add_api_route(
        "/{user_id}/specification",
        test_user_put_spec_handler,
        methods=["PUT"],
        summary="Put test user specification",
        description="Update test user specification by `user_id` and given payload",
    )
    return test_user_router


def _get_emulation_router() -> fastapi.APIRouter:
    emulation_router = fastapi.APIRouter()
    emulation_router.add_api_route(
        "/run/list",
        emulation_run_list_handler,
        methods=["GET"],
        response_model=List[EmulationRunModel],
        summary="Get list of EmulationRun info",
        description="Get list of EmulationRun info by `test_user_id`",
    )
    return emulation_router


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
    app.include_router(_get_feature_router(), dependencies=auth_deps, prefix="/feature", tags=["features"])
    app.include_router(_get_testuser_router(), dependencies=auth_deps, prefix="/test_user", tags=["test_users"])
    app.include_router(_get_testrun_router(), dependencies=auth_deps, prefix="/test_run", tags=["test_runs"])
    app.include_router(_get_emulation_router(), dependencies=auth_deps, prefix="/emulation", tags=["emulations"])

    app.include_router(_get_auth_router())
    app.add_api_route("/", docs, methods=["GET"], include_in_schema=False)
    app.add_api_route("/favicon.ico", favicon, methods=["GET"], include_in_schema=False)
    return app
