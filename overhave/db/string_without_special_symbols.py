import re
from abc import ABC

import sqlalchemy as sa
from sqlalchemy.types import TypeDecorator


class StringWithoutSpecialSymbols(TypeDecorator, ABC):

    impl = sa.String

    def process_bind_param(self, value, dialect):
        if value:
            if re.match(r"^[a-z0-9A-Zа-яА-ЯёЁ]+$", value):
                return value
            raise ValueError("Object shouldn`t contain any special symbols or spaces")

    def copy(self, **kw):
        return StringWithoutSpecialSymbols(self.impl.length)
