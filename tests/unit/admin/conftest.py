from typing import Optional
from uuid import uuid1

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from overhave.admin.views import DraftView, FeatureView, TestRunView
from overhave.admin.views.formatters import _get_button_class_by_status
from overhave.db import TestReportStatus


@pytest.fixture(scope="session")
def test_testrun_view(session_mocker: MockerFixture) -> TestRunView:
    return session_mocker.create_autospec(TestRunView)


@pytest.fixture()
def test_testrun_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_testrun_report_link(report_status: TestReportStatus, faker: Faker) -> Optional[str]:
    if report_status.has_report:
        return None
    return "kek/" + str(uuid1())


@pytest.fixture()
def test_testrun_button_css_class(status: str) -> str:
    return _get_button_class_by_status(status)


@pytest.fixture()
def test_feature_view(test_browse_url: Optional[str], mocker: MockerFixture) -> FeatureView:
    mock = mocker.create_autospec(FeatureView)
    mock.browse_url = test_browse_url
    return mock


@pytest.fixture()
def test_feature_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_feature_name(faker: Faker) -> str:
    return faker.word()


@pytest.fixture(scope="session")
def test_draft_view(session_mocker: MockerFixture) -> DraftView:
    return session_mocker.create_autospec(DraftView)
