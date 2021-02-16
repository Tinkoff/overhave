from uuid import uuid1

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from overhave.admin.views import TestRunView
from overhave.admin.views.formatters import _get_button_class_by_status


@pytest.fixture(scope="session")
def test_testrun_view(session_mocker: MockerFixture) -> TestRunView:
    return session_mocker.create_autospec(TestRunView)


@pytest.fixture()
def test_testrun_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_testrun_report_link(faker: Faker) -> str:
    return "kek/" + str(uuid1())


@pytest.fixture()
def test_testrun_button_css_class(status: str) -> str:
    return _get_button_class_by_status(status)
