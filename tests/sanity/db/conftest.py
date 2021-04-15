from unittest import mock

import click
import pytest

from overhave import OverhaveDBSettings, set_config_to_context


@pytest.fixture()
def click_ctx_mock() -> click.Context:
    return mock.create_autospec(click.Context)


@pytest.fixture()
def set_config_to_ctx(db_settings: OverhaveDBSettings, database: None, click_ctx_mock: click.Context) -> None:
    set_config_to_context(context=click_ctx_mock, settings=db_settings)
