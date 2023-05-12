import logging
import re
from typing import Any, cast

import sqlalchemy
import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapper, Query
from sqlalchemy.orm import Session as SessionClass
from sqlalchemy.orm import as_declarative, declared_attr, scoped_session, sessionmaker

logger = logging.getLogger(__name__)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class SAMetadata(MetaData):
    """Custom SQLAlchemy MetaData with bounded engine."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._bind: sqlalchemy.Engine | None = None

    @property
    def bind(self) -> sqlalchemy.Engine:
        if isinstance(self._bind, sqlalchemy.Engine):
            return self._bind
        raise RuntimeError("MetaData has not got bounded Engine!")

    def set_bind(self, engine: sqlalchemy.Engine) -> None:
        self._bind = engine


metadata = SAMetadata(naming_convention=convention)


def _classname_to_tablename(name: str) -> str:
    result: list[str] = []

    last_index = 0
    for match in re.finditer(r"(?P<abbreviation>[A-Z]+(?![a-z\d]))|(?P<word>[A-Z][a-z]*)|(?P<digit>\d+)", name):
        if match.start() != last_index:
            raise ValueError(f'Could not translate class name "{name}" to table name')

        last_index = match.end()
        result.append(match.group().lower())

    return "_".join(result)


@as_declarative(metadata=metadata)
class BaseTable:
    """Base table class with __tablename__."""

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return _classname_to_tablename(cls.__name__)


class PrimaryKeyWithoutDateMixin:
    """Table mixin with declared attribute `id`."""

    @declared_attr.cascading
    @classmethod
    def id(cls):  # type: ignore[no-untyped-def]
        return sa.Column(f"{getattr(cls, '__tablename__')}_id", sa.Integer(), primary_key=True)


class PrimaryKeyMixin(PrimaryKeyWithoutDateMixin):
    """Table mixin with `id` and `created_at` declared attributes."""

    @declared_attr.cascading
    @classmethod
    def created_at(cls):  # type: ignore[no-untyped-def]
        return sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now())


def _get_query_cls(
    mapper: tuple[type[BaseTable], ...] | Mapper, session: SessionClass  # type: ignore[type-arg]
) -> Query[Any]:
    if mapper:
        m = mapper
        if isinstance(m, tuple):
            m = mapper[0]  # type: ignore[index, assignment]
        if isinstance(m, Mapper):
            m = m.entity

        try:
            return cast(Query[Any], m.__query_cls__(mapper, session))  # type: ignore[union-attr]
        except AttributeError:
            pass

    return Query(mapper, session)  # type: ignore[arg-type]


Session = sessionmaker(query_cls=_get_query_cls)

current_session = scoped_session(Session)
