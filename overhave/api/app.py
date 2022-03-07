import fastapi as fastapi

from overhave.api.views import receive_test_user


def create_overhave_api() -> fastapi.FastAPI:
    router = fastapi.APIRouter(prefix="/api", tags=["test_users"])
    router.add_api_route("/test_users", receive_test_user, methods=["GET", "POST", "UPDATE", "DELETE"])

    app = fastapi.FastAPI()
    app.include_router(router)
    return app
