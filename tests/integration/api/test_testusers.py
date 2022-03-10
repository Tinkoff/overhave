import pytest as pytest
from faker import Faker
from fastapi.testclient import TestClient

from overhave import db
from overhave.entities.converters import TestUserModel


@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestTestUserAPi:
    """Integration tests for Overhave TestUser API."""

    def test_get_user_no_query(self, test_api_client: TestClient, test_user_role: db.Role) -> None:
        response = test_api_client.get("/test_user/")
        assert response.status_code == 400
        assert response.content is not None

    def test_get_user_by_id_empty(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.get(f"/test_user/?user_id={faker.random_int()}")
        assert response.status_code == 400
        assert response.content is not None

    def test_get_user_by_id(self, test_api_client: TestClient, test_testuser: TestUserModel) -> None:
        response = test_api_client.get(f"/test_user/?user_id={test_testuser.id}")
        assert response.status_code == 200
        assert response.json()
        obj = TestUserModel.parse_obj(response.json())
        assert obj == test_testuser

    def test_get_user_by_name_empty(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.get(f"/test_user/?user_name={faker.random_int()}")
        assert response.status_code == 400
        assert response.content is not None

    def test_get_user_by_name(self, test_api_client: TestClient, test_testuser: TestUserModel) -> None:
        response = test_api_client.get(f"/test_user/?user_name={test_testuser.name}")
        assert response.status_code == 200
        assert response.json()
        obj = TestUserModel.parse_obj(response.json())
        assert obj == test_testuser

    def test_get_user_spec_no_query(self, test_api_client: TestClient, test_user_role: db.Role) -> None:
        response = test_api_client.get("/test_user//specification")
        assert response.status_code == 404

    def test_get_user_spec_empty(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.get(f"/test_user/{faker.random_int()}/specification")
        assert response.status_code == 400
        assert response.content is not None

    def test_get_user_spec(self, test_api_client: TestClient, test_testuser: TestUserModel) -> None:
        response = test_api_client.get(f"/test_user/{test_testuser.id}/specification")
        assert response.status_code == 200
        assert response.json() == test_testuser.specification
