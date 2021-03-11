import os
import tempfile
from typing import Callable

import pytest
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
