from typing import List

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from overhave import db
from overhave.storage import FeatureModel, TagModel
from overhave.transport.http.base_client import BearerAuth
from tests.integration.api.conftest import validate_content_null


@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestFeatureAPI:
    """Integration tests for Overhave FeatureTags API."""

    def test_get_feature_by_tag_no_query(
        self, test_api_client: TestClient, test_user_role: db.Role, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(
            "/feature/",
            auth=test_api_bearer_auth,
        )
        assert response.status_code == 400
        validate_content_null(response, False)

    def test_get_feature_by_not_existing_tag_id(
        self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/feature/?tag_id={faker.random_int()}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json() == []

    def test_get_no_feature_by_tag_id(
        self, test_api_client: TestClient, test_tag: TagModel, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/feature/?tag_id={test_tag.id}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json() == []

    def test_get_feature_by_tag_id(
        self,
        test_api_client: TestClient,
        test_tag: TagModel,
        test_feature_with_tag: FeatureModel,
        test_api_bearer_auth: BearerAuth,
    ) -> None:
        response = test_api_client.get(f"/feature/?tag_id={test_tag.id}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json()
        features = parse_obj_as(List[FeatureModel], response.json())
        assert features == [test_feature_with_tag]

    def test_get_feature_by_not_existing_tag_value(
        self, test_api_client: TestClient, faker: Faker, test_user_role: db.Role, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/feature/?tag_value={faker.random_int()}", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    def test_get_no_feature_by_tag_value(
        self, test_api_client: TestClient, test_tag: TagModel, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(f"/feature/?tag_value={test_tag.value}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json() == []

    def test_get_feature_by_tag_value(
        self,
        test_api_client: TestClient,
        test_tag: TagModel,
        test_feature_with_tag: FeatureModel,
        test_api_bearer_auth: BearerAuth,
    ) -> None:
        response = test_api_client.get(f"/feature/?tag_value={test_tag.value}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json()
        features = parse_obj_as(List[FeatureModel], response.json())
        assert features == [test_feature_with_tag]
