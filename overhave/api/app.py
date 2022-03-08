import fastapi as fastapi

from overhave.api.views import test_user_handler


def create_overhave_api() -> fastapi.FastAPI:
    test_user_router = fastapi.APIRouter()
    test_user_router.add_api_route("/", test_user_handler, methods=["GET"])

    app = fastapi.FastAPI()
    app.include_router(test_user_router, prefix="/test_user", tags=["test_users"])
    return app
