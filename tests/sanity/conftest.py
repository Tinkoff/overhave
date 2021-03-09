from typing import Dict, Optional
from unittest import mock

import pytest
from flask import Flask

from overhave.base_settings import DataBaseSettings


@pytest.fixture(scope="module")
def envs_for_mock(db_settings: DataBaseSettings) -> Dict[str, Optional[str]]:
    return {
        "OVERHAVE_DB_URL": str(db_settings.db_url),
    }


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def flask_run_mock(mock_envs: None, database: None) -> mock.MagicMock:
    with mock.patch.object(Flask, "run", return_value=mock.MagicMock()) as flask_run_handler:
        yield flask_run_handler
