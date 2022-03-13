import pytest
from faker import Faker
from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from overhave import db
from overhave.entities.converters import TagModel
from tests.integration.api.conftest import validate_content_null


@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestFeatureTagsAPI:
    """Integration tests for Overhave FeatureTags API."""

    def test_get_tag_by_value_no_body(self, test_api_client: TestClient, test_user_role: db.Role) -> None:
        response = test_api_client.get("/feature/tags/item")
        assert response.status_code == 422
        validate_content_null(response, False)

    def test_get_tag_by_value_empty(self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role) -> None:
        response = test_api_client.get(f"/feature/tags/item?value={faker.word()}")
        assert response.status_code == 400
        validate_content_null(response, False)

    def test_get_tag_by_value(self, test_api_client: TestClient, test_tag: TagModel) -> None:
        response = test_api_client.get(f"/feature/tags/item?value={test_tag.value}")
        assert response.status_code == 200
        assert response.json()
        obj = TagModel.parse_obj(response.json())
        assert obj == test_tag

    def test_get_tags_like_value_no_body(self, test_api_client: TestClient, test_user_role: db.Role) -> None:
        response = test_api_client.get("/feature/tags/list")
        assert response.status_code == 422
        validate_content_null(response, False)

    def test_get_tags_like_value_empty(
        self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role
    ) -> None:
        response = test_api_client.get(f"/feature/tags/list?value={faker.word()}")
        assert response.status_code == 200
        obj = response.json()
        assert obj == []

    def test_get_tags_like_value(self, test_api_client: TestClient, test_tag: TagModel) -> None:
        response = test_api_client.get(f"/feature/tags/list?value={test_tag.value}")
        assert response.status_code == 200
        obj = parse_obj_as(list[TagModel], response.json())
        assert len(obj) == 1
        assert obj[0] == test_tag
