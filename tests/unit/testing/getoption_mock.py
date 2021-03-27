from typing import Any, Mapping


class ConfigGetOptionMock:
    """ The light-weight class for getoption with defined mapping. """

    def __init__(self, mapping: Mapping[str, Any]) -> None:
        self._mapping = mapping

    def getoption(self, *args: Any, **kwargs: Any) -> Any:
        if args:
            return self._mapping.get(args[0])
        return None
