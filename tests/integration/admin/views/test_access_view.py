from http import HTTPStatus

import pytest
from flask.testing import FlaskClient

from overhave import db
from overhave.storage import SystemUserModel


@pytest.mark.usefixtures("database")
class TestAccessView:
    """Tests for access view depending on user role."""

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_get_access_view_admin(self, test_client: FlaskClient, test_authorized_user: SystemUserModel) -> None:
        response = test_client.get("/userrole/")
        assert response.status_code == HTTPStatus.OK
        assert "Access - Users - Overhave" in response.data.decode("utf-8"), "Can't find Access button"

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_access_view_user(self, test_client: FlaskClient, test_authorized_user: SystemUserModel) -> None:
        response = test_client.get("/userrole/")
        assert response.status_code == HTTPStatus.FOUND
        assert 'You should be redirected automatically to the target URL: <a href="/">/</a>' in response.data.decode(
            "utf-8"
        ), "Doesn't redirect to the index page"
