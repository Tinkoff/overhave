from overhave.db.string_without_special_symbols import StringWithoutSpecialSymbols


class TestStringWithoutSpecialSymbols:
    """ Unit tests for :class:`StringWithoutSpecialSymbols`. """

    def test_name(self, test_string_without_special_symbols: StringWithoutSpecialSymbols) -> None:
        assert test_string_without_special_symbols.__class__.__name__ == "String"
        assert test_string_without_special_symbols.length == 256
