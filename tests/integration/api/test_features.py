from typing import List, Optional
from unittest import mock

import allure
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from overhave import db
from overhave.db import TestReportStatus, TestRunStatus
from overhave.storage import FeatureModel, ScenarioModel, TagModel, TestRunStorage
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

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
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

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
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

    def test_run_test_by_tag_handler_absent_tag(
        self,
        test_api_client: TestClient,
        test_api_bearer_auth: BearerAuth,
        test_user_role: db.Role,
        faker: Faker,
    ) -> None:
        response = test_api_client.get(f"/feature/run_test_by_tag/?tag_run={faker.word()}", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_run_test_by_tag_handler_handler(
        self,
        test_api_client: TestClient,
        test_api_bearer_auth: BearerAuth,
        test_tag: TagModel,
        test_scenario_run: ScenarioModel,
        flask_urlfor_handler_mock: mock.MagicMock,
    ) -> None:
        response = test_api_client.get(f"/feature/run_test_by_tag/?tag_run={test_tag.value}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)

    def test_get_test_run_id_handler_not_found(
        self,
        test_api_client: TestClient,
        test_user_role: db.Role,
        test_api_bearer_auth: BearerAuth,
    ) -> None:
        response = test_api_client.get(f"/feature/get_test_run_id/?test_run_id={9999}", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_test_run_id_handler_found_running(
        self,
        test_api_client: TestClient,
        test_user_role: db.Role,
        test_api_bearer_auth: BearerAuth,
        test_run_storage: TestRunStorage,
        test_feature: FeatureModel,
        test_created_test_run_id: int,
    ) -> None:
        test_run_storage.set_run_status(test_created_test_run_id, TestRunStatus.RUNNING)
        response = test_api_client.get(
            f"/feature/get_test_run_id/?test_run_id={test_created_test_run_id}", auth=test_api_bearer_auth
        )
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json()["status"] == TestRunStatus.RUNNING
        assert response.json()["report"] is None

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_test_run_id_handler_found_finished(
        self,
        test_api_client: TestClient,
        test_user_role: db.Role,
        test_api_bearer_auth: BearerAuth,
        test_run_storage: TestRunStorage,
        test_feature: FeatureModel,
        test_created_test_run_id: int,
        test_report: Optional[str],
    ) -> None:
        test_run_storage.set_run_status(test_created_test_run_id, TestRunStatus.SUCCESS)
        test_run_storage.set_report(run_id=test_created_test_run_id, status=TestReportStatus.SAVED, report=test_report)

        response = test_api_client.get(
            f"/feature/get_test_run_id/?test_run_id={test_created_test_run_id}", auth=test_api_bearer_auth
        )
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json()["status"] == TestRunStatus.SUCCESS
        assert response.json()["report"] == test_report
