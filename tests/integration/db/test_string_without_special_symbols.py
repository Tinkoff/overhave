from typing import Callable

import pytest
from faker import Faker
from sqlalchemy.exc import StatementError

from overhave import db


class TestStringWithoutSpecialSymbols:
    """ Unit tests for :class:`StringWithoutSpecialSymbols`. """

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_raises_value_error_if_space(self, test_tags_factory: Callable[[str], None], faker: Faker) -> None:
        with pytest.raises(StatementError):
            test_tags_factory(f"{faker.word()} ")
        with pytest.raises(StatementError):
            test_tags_factory(f" {faker.word()}")

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_raises_value_error_if_special_symbols(
        self, test_tags_factory: Callable[[str], None], faker: Faker
    ) -> None:
        with pytest.raises(StatementError):
            test_tags_factory(f"{faker.word()}#$!")
        with pytest.raises(StatementError):
            test_tags_factory("_")

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_correct_value(self, test_tags_factory: Callable[[str], None], faker: Faker) -> None:
        test_tags_factory(faker.word())
