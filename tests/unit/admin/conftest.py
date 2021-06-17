from typing import Optional, cast
from unittest import mock
from uuid import uuid1

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.python import Metafunc
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from faker import Faker
from pytest_mock import MockerFixture

from overhave import db
from overhave.admin import views
from overhave.admin.views.formatters.helpers import get_button_class_by_status


def _generate_tables_with_views_tests(metafunc: Metafunc):
    table_arg_name = "test_table"
    view_arg_name = "test_view"
    if {table_arg_name, view_arg_name}.issubset(set(metafunc.fixturenames)):
        metafunc.parametrize(
            (table_arg_name, view_arg_name),
            [
                (mock.create_autospec(db.UserRole), mock.create_autospec(views.UserView)),
                (mock.create_autospec(db.GroupRole), mock.create_autospec(views.GroupView)),
                (mock.create_autospec(db.Feature), mock.create_autospec(views.FeatureView)),
                (mock.create_autospec(db.TestRun), mock.create_autospec(views.TestRunView)),
                (mock.create_autospec(db.Draft), mock.create_autospec(views.DraftView)),
                (mock.create_autospec(db.Emulation), mock.create_autospec(views.EmulationView)),
                (mock.create_autospec(db.EmulationRun), mock.create_autospec(views.EmulationRunView)),
                (mock.create_autospec(db.TestUser), mock.create_autospec(views.TestUserView)),
            ],
        )


def pytest_generate_tests(metafunc: Metafunc) -> None:
    _generate_tables_with_views_tests(metafunc)


@pytest.fixture(scope="session")
def test_testrun_view(session_mocker: MockerFixture) -> views.TestRunView:
    return session_mocker.create_autospec(views.TestRunView)


@pytest.fixture(scope="session")
def test_testuser_view(session_mocker: MockerFixture) -> views.TestUserView:
    return session_mocker.create_autospec(views.TestUserView)


@pytest.fixture()
def test_testrun_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_testrun_report(report_status: db.TestReportStatus, faker: Faker) -> Optional[str]:
    if report_status.has_report:
        return uuid1().hex
    return None


@pytest.fixture()
def test_testrun_button_css_class(status: str) -> str:
    return get_button_class_by_status(status)


@pytest.fixture()
def test_feature_view(test_browse_url: Optional[str], mocker: MockerFixture) -> views.FeatureView:
    mock = mocker.create_autospec(views.FeatureView)
    mock.browse_url = test_browse_url
    mock.feature_suffix = ".feature"
    return mock


@pytest.fixture()
def test_feature_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_feature_name(faker: Faker) -> str:
    return faker.word()


@pytest.fixture(scope="session")
def test_draft_view(session_mocker: MockerFixture) -> views.DraftView:
    return session_mocker.create_autospec(views.DraftView)


@pytest.fixture()
def test_prurl(request: FixtureRequest) -> Optional[str]:
    if hasattr(request, "param"):
        return cast(Optional[str], request.param)
    raise NotImplementedError


@pytest.fixture()
def user_role(request: FixtureRequest) -> db.Role:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def current_user_mock(user_role: db.Role, faker: Faker) -> mock.MagicMock:
    with mock.patch("overhave.admin.views.tag.current_user", return_value=mock.MagicMock()) as mocked:
        mocked.login = faker.word()
        mocked.role = user_role
        yield mocked


@pytest.fixture()
def test_tags_view() -> views.TagsView:
    return views.TagsView(model=db.Tags, session=UnifiedAlchemyMagicMock)


@pytest.fixture()
def test_tags_row() -> db.Tags:
    return db.Tags()


@pytest.fixture()
def form_mock(test_incorrect_testing_user_row: db.TestUser) -> mock.MagicMock:
    form_mock = mock.MagicMock()
    form_mock.data = {}
    form_mock._obj = test_incorrect_testing_user_row
    return form_mock


@pytest.fixture()
def test_testing_user_view(faker: Faker) -> views.TestUserView:
    return views.TestUserView(model=db.TestUser, session=UnifiedAlchemyMagicMock)


@pytest.fixture()
def test_testing_user_row() -> db.TestUser:
    return db.TestUser()


@pytest.fixture()
def test_incorrect_testing_user_row(faker: Faker) -> db.TestUser:
    test_user: db.TestUser = db.TestUser()
    test_user.feature_type = db.FeatureType()
    test_user.feature_type.name = faker.word()
    return test_user


@pytest.fixture()
def current_testing_users_user_mock(user_role: db.Role, faker: Faker) -> mock.MagicMock:
    with mock.patch("overhave.admin.views.testing_users.current_user", return_value=mock.MagicMock()) as mocked:
        mocked.login = faker.word()
        mocked.role = user_role
        yield mocked
