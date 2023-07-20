import pytest
from fastapi.testclient import TestClient

from overhave import db
from overhave.storage import FeatureTypeModel
from overhave.transport.http.base_client import BearerAuth
from tests.objects import LIST_FEATURETYPE_MODEL_ADAPTER


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
        obj = LIST_FEATURETYPE_MODEL_ADAPTER.validate_python(response.json())
        assert len(obj) == 1
        assert obj[0] == test_feature_type
