import pytest
from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from overhave import db
from overhave.storage import FeatureTypeModel
from overhave.transport.http.base_client import BearerAuth


@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestFeatureTypesAPI:
    """Integration tests for Overhave FeatureTypes API."""

    def test_get_types(
        self, test_api_client: TestClient, test_feature_type: FeatureTypeModel, test_api_bearer_auth: BearerAuth
    ) -> None:
        response = test_api_client.get(
            "/feature/types/list",
            auth=test_api_bearer_auth,
        )
        assert response.status_code == 200
        obj = parse_obj_as(list[FeatureTypeModel], response.json())
        assert len(obj) == 1
        assert obj[0] == test_feature_type
