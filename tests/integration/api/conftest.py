from typing import Dict, Optional
from unittest import mock

import httpx
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from pydantic.types import SecretStr

from overhave import db, overhave_api
from overhave.storage import AuthStorage, SystemUserModel, SystemUserStorage, TestUserSpecification
from overhave.transport.http.api_client.authenticator import OverhaveApiAuthenticator
from overhave.transport.http.api_client.settings import OverhaveApiAuthenticatorSettings
from overhave.transport.http.base_client import BearerAuth


@pytest.fixture(scope="module")
def envs_for_mock() -> Dict[str, Optional[str]]:
    return {
        "OVERHAVE_API_AUTH_SECRET_KEY": "123",
        "OVERHAVE_FEATURES_DIR": "/features",
        "OVERHAVE_FIXTURES_DIR": "/fixtures",
        "OVERHAVE_STEPS_DIR": "/steps",
    }


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def test_api_client(database) -> TestClient:
    return TestClient(overhave_api())


@pytest.fixture()
def service_system_user(
    test_system_user_storage: SystemUserStorage,
    database,
    faker: Faker,
) -> SystemUserModel:
    return test_system_user_storage.create_user(
        login=f"{faker.word()}.{faker.word()}", password=SecretStr(faker.word()), role=db.Role.admin
    )


@pytest.fixture()
def api_authenticator_settings(test_api_client: TestClient) -> OverhaveApiAuthenticatorSettings:
    return OverhaveApiAuthenticatorSettings(url=test_api_client.base_url)


@pytest.fixture()
def api_authenticator(
    mock_envs, test_api_client: TestClient, api_authenticator_settings: OverhaveApiAuthenticatorSettings
) -> OverhaveApiAuthenticator:
    with mock.patch.object(httpx, "request", new_callable=lambda: test_api_client.request):
        yield OverhaveApiAuthenticator(settings=api_authenticator_settings, auth_storage=AuthStorage())


@pytest.fixture()
def test_api_bearer_auth(
    service_system_user: SystemUserModel, api_authenticator: OverhaveApiAuthenticator
) -> BearerAuth:
    return api_authenticator.get_bearer_auth(username=service_system_user.login, password=service_system_user.password)


@pytest.fixture(scope="module")
def test_new_specification() -> TestUserSpecification:
    return TestUserSpecification({"new_test": "new_value"})


def validate_content_null(response: httpx.Response, statement: bool) -> None:
    assert (response.content.decode() == "null") is statement


@pytest.fixture()
def flask_urlfor_handler_mock(faker: Faker) -> mock.MagicMock:
    with mock.patch("flask.url_for") as flask_urlfor_handler:
        flask_urlfor_handler.return_value = f"/testrun/details/?id={faker.random_int()}"
        yield flask_urlfor_handler
