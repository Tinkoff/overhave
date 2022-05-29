from typing import Dict

from _pytest.nodes import Item


class BasePytestItemsCacheException(Exception):
    """Base exception for :class:`PytestItemsCache`."""


class DuplicateNodeIDError(BasePytestItemsCacheException):
    """Exception for situation with duplicated item nodeid."""


class NodeIDNotFoundError(BasePytestItemsCacheException):
    """Exception for situation with not existing item nodeid."""


class PytestItemsCache:
    """Class for Pytest items caching."""

    def __init__(self) -> None:
        self._items: Dict[str, Item] = {}

    def register_item(self, item: Item) -> None:
        if self._items.get(item.nodeid) is not None:
            raise DuplicateNodeIDError(f"Could not register item in cache: found duplicate nodeid='{item.nodeid}'!")
        self._items[item.nodeid] = item

    def get_item(self, nodeid: str) -> Item:
        item = self._items.get(nodeid)
        if item is None:
            raise NodeIDNotFoundError(f"Could not find item with nodeid='{nodeid}'!")
        return item
