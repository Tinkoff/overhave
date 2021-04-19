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

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value:
            if re.match(r"^[a-z0-9A-Zа-яА-ЯёЁ]+$", value):
                return value
            raise ValueError("Object shouldn`t contain any special symbols or spaces")
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        return value

    def copy(self, **kw: Any) -> Any:
        return StringWithoutSpecialSymbols(self.impl.length)
