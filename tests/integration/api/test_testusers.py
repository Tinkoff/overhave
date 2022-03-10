import json

import pytest as pytest
import requests
from faker import Faker
from fastapi.testclient import TestClient

from overhave import db
from overhave.entities.converters import TestUserModel, TestUserSpecification


def _validate_content_null(response: requests.Response, statement: bool) -> None:
    assert (response.content.decode() == "null") is statement


@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestTestUserAPI:
    """Integration tests for Overhave TestUser API."""

    def test_get_user_no_query(self, test_api_client: TestClient, test_user_role: db.Role) -> None:
        response = test_api_client.get("/test_user/")
        assert response.status_code == 400
        _validate_content_null(response, False)

    def test_get_user_by_id_empty(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.get(f"/test_user/?user_id={faker.random_int()}")
        assert response.status_code == 400
        _validate_content_null(response, False)

    def test_get_user_by_id(self, test_api_client: TestClient, test_testuser: TestUserModel) -> None:
        response = test_api_client.get(f"/test_user/?user_id={test_testuser.id}")
        assert response.status_code == 200
        assert response.json()
        obj = TestUserModel.parse_obj(response.json())
        assert obj == test_testuser

    def test_get_user_by_name_empty(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.get(f"/test_user/?user_name={faker.random_int()}")
        assert response.status_code == 400
        _validate_content_null(response, False)

    def test_get_user_by_name(self, test_api_client: TestClient, test_testuser: TestUserModel) -> None:
        response = test_api_client.get(f"/test_user/?user_name={test_testuser.name}")
        assert response.status_code == 200
        assert response.json()
        obj = TestUserModel.parse_obj(response.json())
        assert obj == test_testuser

    def test_get_user_spec_no_query(self, test_api_client: TestClient, test_user_role: db.Role) -> None:
        response = test_api_client.get("/test_user//specification")
        assert response.status_code == 404
        _validate_content_null(response, False)

    def test_get_user_spec_empty(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.get(f"/test_user/{faker.random_int()}/specification")
        assert response.status_code == 400
        _validate_content_null(response, False)

    def test_get_user_spec(self, test_api_client: TestClient, test_testuser: TestUserModel) -> None:
        response = test_api_client.get(f"/test_user/{test_testuser.id}/specification")
        assert response.status_code == 200
        assert response.json() == test_testuser.specification

    def test_put_user_spec_no_query(self, test_api_client: TestClient, test_user_role: db.Role) -> None:
        response = test_api_client.put("/test_user//specification")
        assert response.status_code == 404
        _validate_content_null(response, False)

    def test_put_user_spec_no_body(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.put(f"/test_user/{faker.random_int()}/specification")
        assert response.status_code == 422
        _validate_content_null(response, False)

    def test_put_user_spec_no_user(
        self,
        test_api_client: TestClient,
        test_new_specification: TestUserSpecification,
        faker: Faker,
        test_user_role: db.Role,
    ) -> None:
        response = test_api_client.put(
            f"/test_user/{faker.random_int()}/specification", data=json.dumps(test_new_specification)
        )
        assert response.status_code == 400
        _validate_content_null(response, False)

    def test_put_user_spec(
        self, test_api_client: TestClient, test_testuser: TestUserModel, test_new_specification: TestUserSpecification
    ) -> None:
        response = test_api_client.put(
            f"/test_user/{test_testuser.id}/specification", data=json.dumps(test_new_specification)
        )
        assert response.status_code == 200
        _validate_content_null(response, True)

        response = test_api_client.get(f"/test_user/{test_testuser.id}/specification")
        assert response.status_code == 200
        assert response.json() == test_new_specification
