from typing import Optional
from unittest import mock

import allure
import pytest
from faker import Faker
from fastapi.testclient import TestClient

from overhave import db
from overhave.db import TestReportStatus, TestRunStatus
from overhave.storage import FeatureModel, ScenarioModel, TagModel, TestRunStorage
from overhave.transport.http import BearerAuth
from tests.integration.api.conftest import validate_content_null


class TestTestRunAPI:
    """Integration tests for Overhave TestRuns API."""

    def test_run_test_by_tag_handler_absent_tag(
        self,
        test_api_client: TestClient,
        test_api_bearer_auth: BearerAuth,
        faker: Faker,
    ) -> None:
        response = test_api_client.post(f"/test_run/create/?tag_value={faker.word()}", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_run_test_by_tag_handler_handler(
        self,
        test_api_client: TestClient,
        test_api_bearer_auth: BearerAuth,
        test_tag: TagModel,
        test_feature_with_tag: FeatureModel,
        test_scenario: ScenarioModel,
        flask_urlfor_handler_mock: mock.MagicMock,
    ) -> None:
        response = test_api_client.post(f"/test_run/create/?tag_value={test_tag.value}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)

    def test_get_test_run_handler_not_found(
        self,
        test_api_client: TestClient,
        test_api_bearer_auth: BearerAuth,
        faker: Faker,
    ) -> None:
        response = test_api_client.get(f"/test_run/?test_run_id={faker.random_int()}", auth=test_api_bearer_auth)
        assert response.status_code == 400
        validate_content_null(response, False)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_test_run_handler_found_running(
        self,
        test_run_storage: TestRunStorage,
        test_api_client: TestClient,
        test_api_bearer_auth: BearerAuth,
        test_created_test_run_id: int,
    ) -> None:
        test_run_storage.set_run_status(test_created_test_run_id, TestRunStatus.RUNNING)
        response = test_api_client.get(f"/test_run/?test_run_id={test_created_test_run_id}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json()["status"] == TestRunStatus.RUNNING
        assert response.json()["report"] is None

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_test_run_handler_found_finished(
        self,
        test_run_storage: TestRunStorage,
        test_api_client: TestClient,
        test_api_bearer_auth: BearerAuth,
        test_created_test_run_id: int,
        test_report: Optional[str],
    ) -> None:
        test_run_storage.set_run_status(test_created_test_run_id, TestRunStatus.SUCCESS)
        test_run_storage.set_report(run_id=test_created_test_run_id, status=TestReportStatus.SAVED, report=test_report)

        response = test_api_client.get(f"/test_run/?test_run_id={test_created_test_run_id}", auth=test_api_bearer_auth)
        assert response.status_code == 200
        validate_content_null(response, False)
        assert response.json()["status"] == TestRunStatus.SUCCESS
        assert response.json()["report"] == test_report
