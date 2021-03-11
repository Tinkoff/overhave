from pathlib import Path
from uuid import uuid1

import pytest
from faker import Faker

from overhave.factory import ProxyFactory


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
