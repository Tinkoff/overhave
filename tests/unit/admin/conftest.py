from typing import cast
from unittest import mock
from unittest.mock import patch
from uuid import uuid1

import allure
import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.python import Metafunc
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from faker import Faker
from pytest_mock import MockerFixture

from overhave import db
from overhave.admin import views
from overhave.admin.views.formatters.helpers import get_button_class_by_status
from overhave.factory import IAdminFactory
from overhave.utils import get_current_time


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
def test_testrun_report(report_status: db.TestReportStatus, faker: Faker) -> str | None:
    if report_status.has_report:
        return uuid1().hex
    return None


@pytest.fixture()
def test_testrun_button_css_class(status: str) -> str:
    return get_button_class_by_status(status)


@pytest.fixture()
def test_feature_view_mocked(task_tracker_url: str | None, mocker: MockerFixture) -> views.FeatureView:
    mock = mocker.create_autospec(views.FeatureView)
    mock.task_tracker_url = task_tracker_url
    mock.feature_suffix = ".feature"
    return mock


@pytest.fixture()
def test_feature_view(patched_admin_factory: IAdminFactory) -> views.FeatureView:
    return views.FeatureView(model=db.Feature, session=UnifiedAlchemyMagicMock)


@pytest.fixture()
def test_feature_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_feature_name(faker: Faker) -> str:
    return faker.word()


@pytest.fixture()
def test_feature_model_task() -> list[str]:
    return ["KEK-1111"]


@pytest.fixture()
def test_feature_type_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_system_user_login(faker: Faker) -> str:
    return faker.word()


@pytest.fixture()
def test_feature_filepath(request: FixtureRequest, faker: Faker) -> str:
    if hasattr(request, "param") and isinstance(request.param, str):
        return request.param
    return faker.word()


@pytest.fixture()
def test_severity(faker: Faker) -> allure.severity_level:
    lst = list(allure.severity_level)
    return lst[faker.random_int(0, len(lst) - 1)]


@pytest.fixture()
def test_feature_row(
    faker: Faker,
    test_feature_id: int,
    test_feature_name: str,
    test_system_user_login: str,
    test_feature_type_id: int,
    test_feature_filepath: str,
    test_severity: allure.severity_level,
    test_feature_model_task: list[str],
) -> db.Feature:
    row = db.Feature(
        name=test_feature_name,
        author=test_system_user_login,
        type_id=test_feature_type_id,
        file_path=test_feature_filepath,
        task=test_feature_model_task,
        severity=test_severity,
        last_edited_at=get_current_time(),
    )
    row.id = test_feature_id
    return row


@pytest.fixture()
def test_draft_row(
    faker: Faker, test_feature_id: int, test_testrun_id: int, test_feature_row: db.Feature, test_system_user_login: str
) -> db.Draft:
    row = db.Draft(
        feature_id=test_feature_id,
        test_run_id=test_testrun_id,
        text=faker.word(),
        published_by=test_system_user_login,
        status=db.DraftStatus.REQUESTED,
    )
    row.feature = test_feature_row
    return row


@pytest.fixture(scope="session")
def test_draft_view(session_mocker: MockerFixture) -> views.DraftView:
    return session_mocker.create_autospec(views.DraftView)


@pytest.fixture(scope="session")
def test_not_mocked_draft_view() -> views.DraftView:
    return views.DraftView(model=db.Draft, session=UnifiedAlchemyMagicMock)


@pytest.fixture()
def test_prurl(request: FixtureRequest) -> str | None:
    if hasattr(request, "param"):
        return cast(str | None, request.param)
    raise NotImplementedError


@pytest.fixture()
def user_role(request: FixtureRequest) -> db.Role:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_tags_view() -> views.TagsView:
    return views.TagsView(model=db.Tags, session=UnifiedAlchemyMagicMock)


@pytest.fixture()
def test_tags_row(faker: Faker, test_system_user_login: str) -> db.Tags:
    return db.Tags(value=faker.word(), created_by=faker.word())


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
    test_user: db.TestUser = db.TestUser(feature_type=db.FeatureType(name=faker.word()))
    return test_user


@pytest.fixture()
def current_user_mock(user_role: db.Role, faker: Faker, test_mock_patch_user_directory: str) -> mock.MagicMock:
    with mock.patch(test_mock_patch_user_directory, return_value=mock.MagicMock()) as mocked:
        mocked.login = faker.word()
        mocked.role = user_role
        yield mocked


@pytest.fixture()
def test_mock_patch_user_directory(request: FixtureRequest) -> list[str]:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_mock_admin_factory() -> mock.MagicMock:
    with patch("overhave.admin.views.feature.get_admin_factory", return_value=mock.MagicMock()) as mocked:
        instance = mocked.return_value
        instance.context.file_settings.feature_suffix = ".feature"
        yield mocked
