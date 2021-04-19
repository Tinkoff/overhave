from typing import Callable

import pytest
from sqlalchemy.exc import StatementError

from overhave import db
from overhave.entities.converters import TagsTypeModel


class TestStringWithoutSpecialSymbols:
    """ Unit tests for :class:`StringWithoutSpecialSymbols`. """

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_raises_value_error_if_space(self, test_tags_with_spaces: Callable[[], TagsTypeModel]) -> None:
        with pytest.raises(StatementError):
            test_tags_with_spaces()

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_raises_value_error_if_special_symbols(
        self, test_tags_with_special_symbols: Callable[[], TagsTypeModel]
    ) -> None:
        with pytest.raises(StatementError):
            test_tags_with_special_symbols()

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_correct_value(self, test_correct_tags: Callable[[], TagsTypeModel]) -> None:
        test_correct_tags()
