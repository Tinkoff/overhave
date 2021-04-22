import re
from typing import Any

import sqlalchemy as sa
from sqlalchemy.types import TypeDecorator


class StringWithoutSpecialSymbols(TypeDecorator):
    """ String without any special characters. """

    impl = sa.String

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__class__.__name__ = "String"
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value: Any, dialect: Any) -> str:
        if isinstance(value, str) and re.match(r"^[a-z0-9A-Zа-яА-ЯёЁ_]+$", value):
            return value
        raise ValueError("Object shouldn`t contain any special symbols or spaces")

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        return value

    def copy(self, **kw: Any) -> Any:
        return StringWithoutSpecialSymbols(self.impl.length)
