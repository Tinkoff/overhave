from faker import Faker
from fastapi.testclient import TestClient
from pydantic.types import SecretStr

from overhave.api import AuthToken
from overhave.api.settings import OverhaveApiAuthSettings
from overhave.storage import SystemUserModel
from overhave.transport.http.api_client.authenticator import OverhaveApiAuthenticator
from overhave.transport.http.api_client.models import TokenRequestData
from overhave.transport.http.base_client import BearerAuth
from overhave.utils import get_current_time
from tests.integration.api.conftest import validate_content_null


class TestAuthAPI:
    """Integration tests for Overhave API auth_managers."""

    def test_unathorized(self, test_api_client: TestClient) -> None:
        response = test_api_client.get("/test_user/")
        assert response.status_code == 401
        validate_content_null(response, False)

    def test_create_token_no_body(
        self, test_api_client: TestClient, api_authenticator: OverhaveApiAuthenticator
    ) -> None:
        response = test_api_client.post("/token")
        assert response.status_code == 422
        validate_content_null(response, False)

    def test_create_token_no_user(
        self, test_api_client: TestClient, api_authenticator: OverhaveApiAuthenticator, faker: Faker
    ) -> None:
        data = TokenRequestData(username=faker.word(), password=faker.word())
        response = test_api_client.post("/token", data=data.dict(by_alias=True))
        assert response.status_code == 401
        validate_content_null(response, False)

    def test_create_token(
        self,
        test_api_client: TestClient,
        api_authenticator: OverhaveApiAuthenticator,
        service_system_user: SystemUserModel,
    ) -> None:
        password = service_system_user.password or SecretStr("")
        data = TokenRequestData(username=service_system_user.login, password=password.get_secret_value())
        response = test_api_client.post("/token", data=data.dict(by_alias=True))
        assert response.status_code == 200
        validate_content_null(response, False)
        token = AuthToken.parse_obj(response.json())
        assert token.access_token
        settings_expire_timedelta = OverhaveApiAuthSettings().access_token_expire_timedelta
        assert get_current_time() < token.expires_at < get_current_time() + settings_expire_timedelta

    def test_interact_with_incorrect_token(
        self, test_api_client: TestClient, api_authenticator: OverhaveApiAuthenticator, faker: Faker
    ) -> None:
        response = test_api_client.get("/test_user/", auth=BearerAuth(faker.word()))
        assert response.status_code == 401
        validate_content_null(response, False)
