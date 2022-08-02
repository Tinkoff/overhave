import json

import pytest as pytest
from faker import Faker
from fastapi.testclient import TestClient
from pydantic.tools import parse_obj_as

from overhave import db
from overhave.storage import TestUserModel, TestUserSpecification
from overhave.transport.http.base_client import BearerAuth
from tests.integration.api.conftest import validate_content_null


class TestTestUserAPI:
    """Integration tests for Overhave TestUser API."""

    def test_get_user_no_query(self, test_api_client: TestClient, test_api_bearer_auth: BearerAuth) -> None:
        response = test_api_client.get("/test_user/", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    def test_get_user_by_id_empty(
        self, test_api_client: TestClient, test_api_bearer_auth: BearerAuth, faker: Faker
    ) -> None:
        response = test_api_client.get(f"/test_user/?user_id={faker.random_int()}", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_user_by_id(
        self, test_api_client: TestClient, test_testuser: TestUserModel, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/test_user/?user_id={test_testuser.id}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        assert response.json()
        obj = TestUserModel.parse_obj(response.json())
        assert obj == test_testuser

    def test_get_user_by_name_empty(
        self, test_api_client: TestClient, faker: Faker, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/test_user/?user_name={faker.random_int()}", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_user_by_name(
        self, test_api_client: TestClient, test_testuser: TestUserModel, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/test_user/?user_name={test_testuser.name}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        assert response.json()
        obj = TestUserModel.parse_obj(response.json())
        assert obj == test_testuser

    def test_get_user_list_no_query(self, test_api_client: TestClient, test_api_bearer_auth: BearerAuth) -> None:
        response = test_api_client.get("/test_user/list", auth=test_api_bearer_auth)
        assert response.status_code == 422
        validate_content_null(response, False)

    @pytest.mark.parametrize("allow_update", [True, False])
    def test_get_test_user_list_feature_type_empty(
        self, test_api_client: TestClient, faker: Faker, test_api_bearer_auth: BearerAuth, allow_update: bool
    ) -> None:
        response = test_api_client.get(
            f"/test_user/list?feature_type={faker.word()}&allow_update={str(allow_update)}",
            auth=test_api_bearer_auth,
        )
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_test_user_list(
        self, test_api_client: TestClient, test_testuser: TestUserModel, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(
            f"/test_user/list?feature_type={test_testuser.feature_type.name}&allow_update={test_testuser.allow_update}",
            auth=test_api_bearer_auth,
        )
        assert response.status_code == 200
        obj = parse_obj_as(list[TestUserModel], response.json())
        assert len(obj) == 1
        assert obj[0] == test_testuser

    def test_get_user_spec_no_query(self, test_api_client: TestClient) -> None:
        response = test_api_client.get("/test_user//specification")
        assert response.status_code == 404
        validate_content_null(response, False)

    def test_get_user_spec_empty(
        self, test_api_client: TestClient, faker: Faker, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/test_user/{faker.random_int()}/specification", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_user_spec(
        self, test_api_client: TestClient, test_testuser: TestUserModel, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/test_user/{test_testuser.id}/specification", auth=test_api_bearer_auth)
        assert response.status_code == 200
        assert response.json() == test_testuser.specification

    def test_put_user_spec_no_query(self, test_api_client: TestClient) -> None:
        response = test_api_client.put("/test_user//specification")
        assert response.status_code == 404
        validate_content_null(response, False)

    def test_put_user_spec_no_body(
        self, test_api_client: TestClient, faker: Faker, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.put(f"/test_user/{faker.random_int()}/specification", auth=test_api_bearer_auth)
        assert response.status_code == 422
        validate_content_null(response, False)

    def test_put_user_spec_no_user(
        self,
        test_api_client: TestClient,
        test_new_specification: TestUserSpecification,
        faker: Faker,
        test_api_bearer_auth: BearerAuth,
    ) -> None:
        response = test_api_client.put(
            f"/test_user/{faker.random_int()}/specification",
            auth=test_api_bearer_auth,
            data=json.dumps(test_new_specification),
        )
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("testuser_allow_update", [False], indirect=True)
    def test_put_user_spec_not_allowed(
        self,
        test_api_client: TestClient,
        test_testuser: TestUserModel,
        test_new_specification: TestUserSpecification,
        test_api_bearer_auth: BearerAuth,
    ) -> None:
        response = test_api_client.put(
            f"/test_user/{test_testuser.id}/specification",
            auth=test_api_bearer_auth,
            data=json.dumps(test_new_specification),
        )
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("testuser_allow_update", [True], indirect=True)
    def test_put_user_spec(
        self,
        test_api_client: TestClient,
        test_testuser: TestUserModel,
        test_new_specification: TestUserSpecification,
        test_api_bearer_auth: BearerAuth,
    ) -> None:
        response = test_api_client.put(
            f"/test_user/{test_testuser.id}/specification",
            auth=test_api_bearer_auth,
            data=json.dumps(test_new_specification),
        )
        assert response.status_code == 200
        validate_content_null(response, True)

        response = test_api_client.get(
            f"/test_user/{test_testuser.id}/specification",
            auth=test_api_bearer_auth,
        )
        assert response.status_code == 200
        assert response.json() == test_new_specification
