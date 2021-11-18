from unittest import mock

import pytest
from faker import Faker

from overhave.pytest_plugin import DescriptionManager


@pytest.mark.parametrize("enable_html", [True, False])
class TestDescriptionManager:
    """Unit tests for DescriptionManager."""

    def test_add_description(self, test_description_manager: DescriptionManager, faker: Faker) -> None:
        assert not test_description_manager._description
        test_description_manager.add_description(faker.word())
        assert len(test_description_manager._description) == 1

    def test_add_description_above(self, test_description_manager: DescriptionManager, faker: Faker) -> None:
        test_description_manager.add_description(faker.word())
        above_block = faker.word()
        test_description_manager.add_description_above(above_block)
        assert len(test_description_manager._description) == 2
        assert above_block == test_description_manager._description[0]

    def test_apply_empty_description(
        self, test_description_manager: DescriptionManager, description_handler_mock: mock.MagicMock
    ) -> None:
        test_description_manager.apply_description()
        description_handler_mock.assert_not_called()

    def test_apply_description(
        self, test_description_manager: DescriptionManager, faker: Faker, description_handler_mock: mock.MagicMock
    ) -> None:
        test_description_manager.add_description(faker.word())
        test_description_manager.apply_description()
        description_handler_mock.assert_called_once()
