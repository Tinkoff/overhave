from http import HTTPStatus

from flask import Response
from flask.testing import FlaskClient
from wtforms import Form

from overhave import OverhaveAppType, db
from overhave.admin.views import TagsView


class TestTag:
    """ Integration tests for Tags. """

    def test_get_tag(
        self,
        test_app: OverhaveAppType,
        test_client: FlaskClient,
        db_create_user,
        db_create_tag,
        is_accessible_mock,
        current_user_mock,
    ):
        response: Response = test_client.get("/tags/edit/?id=1")
        assert TagsView.on_model_change(self, form=Form, model=db.Tags, is_created=False) is None
        assert response.status_code == HTTPStatus.OK
