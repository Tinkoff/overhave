from http import HTTPStatus
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid1

import pytest
from faker import Faker
from flask import Response
from flask.testing import FlaskClient

from overhave import OverhaveAdminApp
from overhave.admin.views.formatters.helpers import get_report_index_link


class TestAppCommon:
    """ Integration tests for OverhaveApp. """

    def test_app_root_get(self, test_client: FlaskClient) -> None:  # type: ignore
        response: Response = test_client.get("/")
        assert response.status_code == HTTPStatus.FOUND

    def test_app_get_favicon(self, test_app: OverhaveAdminApp, test_client: FlaskClient) -> None:  # type: ignore
        response: Response = test_client.get("/favicon.ico")
        assert response.status_code == HTTPStatus.OK
        assert response.mimetype == "image/vnd.microsoft.icon"
        assert response.data == (Path(test_app.config["FILES_DIR"]) / "favicon.ico").read_bytes()

    def test_app_create_pr_without_publisher(
        self, test_app: OverhaveAdminApp, test_client: FlaskClient, test_pullrequest_id: int  # type: ignore
    ) -> None:
        response: Response = test_client.get(f"/pull_request/{test_pullrequest_id}")
        assert response.status_code == HTTPStatus.FOUND

    def test_app_create_pr_incorrect_data(
        self,
        test_app: OverhaveAdminApp,
        test_client: FlaskClient,  # type: ignore
        test_pullrequest_id: int,
        test_pullrequest_published_by: str,
    ) -> None:
        response: Response = test_client.get(
            f"/pull_request/{test_pullrequest_id}?published_by={test_pullrequest_published_by}"
        )
        assert response.status_code == HTTPStatus.FOUND

    def test_app_get_emulation_run(
        self, test_app: OverhaveAdminApp, test_client: FlaskClient,  # type: ignore
    ) -> None:
        response: Response = test_client.get("http://localhost/emulations/kek:8000")
        assert response.status_code == HTTPStatus.FOUND


class TestAppReport:
    """ Integration tests for OverhaveApp::get_report. """

    def test_app_get_report_notexists(self, test_client: FlaskClient) -> None:  # type: ignore
        response: Response = test_client.get(get_report_index_link(uuid1().hex))
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_app_get_report_noindex(
        self, test_client: FlaskClient, test_report_without_index: Path  # type: ignore
    ) -> None:
        response: Response = test_client.get(get_report_index_link(test_report_without_index.name))
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_app_get_report(self, test_client: FlaskClient, test_report_with_index: Path) -> None:  # type: ignore
        response: Response = test_client.get(get_report_index_link(test_report_with_index.name))
        assert response.status_code == HTTPStatus.OK
        assert response.data == (test_report_with_index / "index.html").read_bytes()

    @pytest.mark.parametrize("data", [None])
    def test_app_post_report_without_run_id(
        self, test_client: FlaskClient, test_report_without_index: Path, data: Optional[Dict[str, str]]  # type: ignore
    ) -> None:
        response: Response = test_client.post(get_report_index_link(test_report_without_index.name), data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.parametrize("data", [{"run_id": "123"}])
    def test_app_post_report_notexists(
        self, test_client: FlaskClient, test_report_without_index: Path, data: Optional[Dict[str, str]]  # type: ignore
    ) -> None:
        response: Response = test_client.post(get_report_index_link(test_report_without_index.name), data=data)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_app_post_report(
        self, test_client: FlaskClient, test_report_with_index: Path, faker: Faker  # type: ignore
    ) -> None:
        response: Response = test_client.post(
            get_report_index_link(test_report_with_index.name), data={"run_id": faker.random_int()}
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == (test_report_with_index / "index.html").read_bytes()
