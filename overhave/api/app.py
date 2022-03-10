import fastapi as fastapi

from overhave.api.views import test_user_get_spec_handler, test_user_handler, test_user_put_spec_handler


def create_overhave_api() -> fastapi.FastAPI:
    test_user_router = fastapi.APIRouter()
    test_user_router.add_api_route(
        "/",
        test_user_handler,
        methods=["GET"],
        summary="Get TestUser",
        description="Get TestUserModel by 'user_id' or 'user_name'",
    )
    test_user_router.add_api_route(
        "/{user_id}/specification",
        test_user_get_spec_handler,
        methods=["GET"],
        summary="Get TestUser specification",
        description="Get TestUserModel.specification by 'user_id'",
    )
    test_user_router.add_api_route(
        "/{user_id}/specification",
        test_user_put_spec_handler,
        methods=["PUT"],
        summary="Put TestUser specification",
        description="Update TestUser.specification by 'user_id' and given payload",
    )

    app = fastapi.FastAPI()
    app.include_router(test_user_router, prefix="/test_user", tags=["test_users"])
    return app
