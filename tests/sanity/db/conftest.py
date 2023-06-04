from unittest import mock

import pytest
import typer

from overhave import OverhaveDBSettings, set_config_to_context
from tests.db_utils import create_test_session


@pytest.fixture()
def typer_ctx_mock() -> typer.Context:
    return mock.create_autospec(typer.Context)


@pytest.fixture()
def set_config_to_ctx(db_settings: OverhaveDBSettings, database: None, typer_ctx_mock: typer.Context) -> None:
    with create_test_session():
        set_config_to_context(context=typer_ctx_mock, settings=db_settings)
        yield
