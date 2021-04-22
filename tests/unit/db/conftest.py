import pytest

from overhave.db.string_without_special_symbols import StringWithoutSpecialSymbols


@pytest.fixture()
def test_string_without_special_symbols() -> StringWithoutSpecialSymbols:
    return StringWithoutSpecialSymbols(256)
