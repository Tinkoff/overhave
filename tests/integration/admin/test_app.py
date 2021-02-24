from http import HTTPStatus
from pathlib import Path

from flask import Response
from flask.testing import FlaskClient

from overhave import OverhaveAppType


class TestApp:
    """ Integration tests for OverhaveApp. """

    def test_app_root_get(self, test_client: FlaskClient):
        response: Response = test_client.get("/")
        assert response.status_code == HTTPStatus.FOUND

    def test_app_get_favicon(self, test_app: OverhaveAppType, test_client: FlaskClient):
        response: Response = test_client.get("/favicon.ico")
        assert response.status_code == HTTPStatus.OK
        assert response.mimetype == "image/vnd.microsoft.icon"
        assert response.data == (Path(test_app.config["FILES_DIR"]) / "favicon.ico").read_bytes()
