import pytest
from _pytest.nodes import Item
from faker import Faker

from overhave.pytest_plugin.items_cache import DuplicateNodeIDError, NodeIDNotFoundError, PytestItemsCache


class TestItemsCache:
    """Unit tests for :class:`PytestItemsCache`."""

    def test_register_item(self, test_items_cache: PytestItemsCache, test_clean_item: Item) -> None:
        test_items_cache.register_item(test_clean_item)
        assert test_items_cache._items[test_clean_item.nodeid] == test_clean_item

    def test_register_duplicate(self, test_items_cache: PytestItemsCache, test_clean_item: Item) -> None:
        test_items_cache.register_item(test_clean_item)
        with pytest.raises(DuplicateNodeIDError):
            test_items_cache.register_item(test_clean_item)

    def test_get_item(self, test_items_cache: PytestItemsCache, test_clean_item: Item) -> None:
        test_items_cache._items[test_clean_item.nodeid] = test_clean_item
        assert test_items_cache.get_item(test_clean_item.nodeid) == test_clean_item

    def test_get_not_exists_item(self, test_items_cache: PytestItemsCache, faker: Faker) -> None:
        with pytest.raises(NodeIDNotFoundError):
            test_items_cache.get_item(faker.word())
