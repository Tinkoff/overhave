import os
import tempfile
from pathlib import Path
from typing import Callable
from uuid import uuid1

import pytest
from faker import Faker
from flask.testing import FlaskClient

from overhave import OverhaveAdminApp, overhave_app
from overhave.base_settings import DataBaseSettings
from overhave.factory import IAdminFactory
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.pytest_plugin import IProxyManager


@pytest.fixture()
def patched_app_admin_factory(
    db_settings: DataBaseSettings,
    database: None,
    mocked_context: BaseFactoryContext,
    clean_admin_factory: Callable[[], IAdminFactory],
) -> IAdminFactory:
    db_settings.setup_db()
    factory = clean_admin_factory()
    factory.set_context(mocked_context)
    return factory


@pytest.fixture()
def test_pullrequest_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_pullrequest_published_by() -> str:
    return uuid1().hex


@pytest.fixture()
def test_report_without_index(patched_app_admin_factory: IAdminFactory) -> Path:
    report_dir = patched_app_admin_factory.context.file_settings.tmp_reports_dir / uuid1().hex
    report_dir.mkdir()
    return report_dir


@pytest.fixture()
def test_report_with_index(test_report_without_index: Path, faker: Faker) -> Path:
    report_index = test_report_without_index / "index.html"
    report_index.write_text(faker.word())
    yield test_report_without_index
    report_index.unlink()


@pytest.fixture()
def test_app(
    clean_proxy_manager: Callable[[], IProxyManager], patched_app_admin_factory: IAdminFactory
) -> OverhaveAdminApp:
    return overhave_app(factory=patched_app_admin_factory)


@pytest.fixture()
def test_client(test_app: OverhaveAdminApp) -> FlaskClient:
    db_fd, test_app.config["DATABASE"] = tempfile.mkstemp()
    test_app.config["TESTING"] = True

    with test_app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(test_app.config["DATABASE"])
