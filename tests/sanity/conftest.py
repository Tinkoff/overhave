from unittest import mock

import pytest
from flask import Flask


@pytest.fixture(scope="class")
def flask_run_mock() -> mock.MagicMock:
    with mock.patch.object(Flask, "run", return_value=mock.MagicMock()) as flask_run_handler:
        yield flask_run_handler
