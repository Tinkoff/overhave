import pytest
from faker import Faker
from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from overhave import db
from overhave.storage import EmulationRunModel, TestUserModel
from overhave.transport.http.base_client import BearerAuth
from tests.integration.api.conftest import validate_content_null


class TestEmulationsAPI:
    """Integration tests for Overhave Emulation API."""

    def test_get_emulation_run_list_no_body(
        self, test_api_client: TestClient, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(
            "/emulation/run/list",
            auth=test_api_bearer_auth,
        )
        assert response.status_code == 422
        validate_content_null(response, False)

    def test_get_emulation_run_list_by_test_user_id_empty(
        self, test_api_client: TestClient, faker: Faker, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(
            f"/emulation/run/list?test_user_id={faker.random_int()}",
            auth=test_api_bearer_auth,
        )
        assert response.status_code == 200
        validate_content_null(response, False)
        assert not response.json()

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_emulation_run_list_by_test_user_id(
        self,
        test_api_client: TestClient,
        test_testuser: TestUserModel,
        test_emulation_run: EmulationRunModel,
        test_api_bearer_auth: BearerAuth,
    ) -> None:
        response = test_api_client.get(
            f"/emulation/run/list?test_user_id={test_testuser.id}",
            auth=test_api_bearer_auth,
        )
        assert response.status_code == 200
        obj = parse_obj_as(list[EmulationRunModel], response.json())
        assert len(obj) == 1
        assert obj[0] == test_emulation_run
