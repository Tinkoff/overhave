import os

import pytest
from flask.testing import FlaskClient

from overhave import OverhaveAdminApp


@pytest.fixture(scope="module")
def mock_support_chat_url() -> None:
    os.environ["TEST_SUPPORT_CHAT_URL"] = "https://localhost"
    return


@pytest.mark.usefixtures("database")
class TestLoginView:
    """Tests for login view."""

    def test_show_flash_with_chat_for_unregistered_user(
        self,
        test_app: OverhaveAdminApp,
        test_client: FlaskClient,
        mock_support_chat_url: None,
    ) -> None:
        test_app.config["WTF_CSRF_ENABLED"] = False

        response = test_client.post("/login", data={"username": "kek", "password": "12345"}, follow_redirects=True)

        assert (
            "Username 'kek' is not registered! Please contact the <a href='https://localhost'>support channel</a>!"
            in response.data.decode("utf-8")
        ), '"Unauthorized" flash not be showed'

    def test_show_flash_without_chat_for_unregistered_user(
        self,
        test_app: OverhaveAdminApp,
        test_client: FlaskClient,
    ) -> None:
        test_app.config["WTF_CSRF_ENABLED"] = False

        response = test_client.post("/login", data={"username": "kek", "password": "12345"}, follow_redirects=True)

        assert "Username 'kek' is not registered!" in response.data.decode(
            "utf-8"
        ), '"Unauthorized" flash not be showed'
