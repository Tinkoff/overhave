from unittest import mock

import pytest
import typer

from overhave import OverhaveDBSettings, set_config_to_context


@pytest.fixture()
def typer_ctx_mock() -> typer.Context:
    return mock.create_autospec(typer.Context)


@pytest.fixture()
def set_config_to_ctx(db_settings: OverhaveDBSettings, database: None, typer_ctx_mock: typer.Context) -> None:
    set_config_to_context(context=typer_ctx_mock, settings=db_settings)
