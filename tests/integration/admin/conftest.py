import os
import tempfile
from pathlib import Path
from typing import Callable
from uuid import uuid1

import pytest
from faker import Faker
from flask.testing import FlaskClient

from overhave import OverhaveAppType, OverhaveContext, overhave_app
from overhave.base_settings import DataBaseSettings
from overhave.factory import ProxyFactory


@pytest.fixture()
def patched_app_proxy_factory(
    db_settings: DataBaseSettings,
    database: None,
    mocked_context: OverhaveContext,
    clean_proxy_factory: Callable[[], ProxyFactory],
) -> ProxyFactory:
    db_settings.setup_db()
    factory = clean_proxy_factory()
    factory.set_context(mocked_context)
    return factory


@pytest.fixture()
def test_app(patched_app_proxy_factory) -> OverhaveAppType:
    return overhave_app(factory=patched_app_proxy_factory)


@pytest.fixture()
def test_client(test_app: OverhaveAppType) -> FlaskClient:
    db_fd, test_app.config["DATABASE"] = tempfile.mkstemp()
    test_app.config["TESTING"] = True

    with test_app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(test_app.config["DATABASE"])


@pytest.fixture()
def test_pullrequest_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_pullrequest_published_by() -> str:
    return uuid1().hex


@pytest.fixture()
def test_report_without_index(patched_app_proxy_factory: ProxyFactory) -> Path:
    report_dir = patched_app_proxy_factory.context.file_settings.tmp_reports_dir / uuid1().hex
    report_dir.mkdir()
    return report_dir


@pytest.fixture()
def test_report_with_index(test_report_without_index: Path, faker: Faker) -> Path:
    report_index = test_report_without_index / "index.html"
    report_index.write_text(faker.word())
    yield test_report_without_index
    report_index.unlink()
