import fastapi as fastapi

from overhave.api.views import get_test_user


def create_overhave_api() -> fastapi.FastAPI:
    test_user_router = fastapi.APIRouter()
    test_user_router.add_api_route("/{user_id}", get_test_user, methods=["GET"])

    app = fastapi.FastAPI()
    app.include_router(test_user_router, prefix="/test_user", tags=["test_users"])
    return app
