import logging
import re
from typing import Any, cast

import sqlalchemy as sa
import sqlalchemy.engine as se
import sqlalchemy.orm as so

logger = logging.getLogger(__name__)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class SAMetadata(sa.MetaData):
    """Custom SQLAlchemy MetaData with bounded engine."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._engine: se.Engine | None = None  # SQLAlchemy2.0 - sa.Engine

    @property
    def engine(self) -> se.Engine:  # SQLAlchemy2.0 - sa.Engine
        if isinstance(self._engine, se.Engine):  # SQLAlchemy2.0 - sa.Engine
            return self._engine
        raise RuntimeError("MetaData has not got bounded Engine!")

    def set_engine(self, engine: se.Engine) -> None:  # SQLAlchemy2.0 - sa.Engine
        self._engine = engine


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


@so.as_declarative(metadata=metadata)
class BaseTable:
    """Base table class with __tablename__."""

    @so.declared_attr  # SQLAlchemy2.0 - @so.declared_attr.directive
    def __tablename__(cls) -> str:
        return _classname_to_tablename(cls.__name__)


class PrimaryKeyWithoutDateMixin:
    """Table mixin with declared attribute `id`."""

    @so.declared_attr.cascading
    def id(cls):  # type: ignore[no-untyped-def]
        return sa.Column(f"{getattr(cls, '__tablename__')}_id", sa.Integer(), primary_key=True)


class PrimaryKeyMixin(PrimaryKeyWithoutDateMixin):
    """Table mixin with `id` and `created_at` declared attributes."""

    @so.declared_attr.cascading
    def created_at(cls):  # type: ignore[no-untyped-def]
        return sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now())


def _get_query_cls(
    mapper: tuple[type[BaseTable], ...] | so.Mapper,  # type: ignore[type-arg]
    session: Any,  # SQLAlchemy2.0 - session: so.SessionClass
) -> so.Query:  # type: ignore[type-arg]  # SQLAlchemy2.0 - so.Query[Any]
    if mapper:
        m = mapper
        if isinstance(m, tuple):
            m = mapper[0]  # type: ignore[index, assignment]
        if isinstance(m, so.Mapper):
            m = m.entity

        try:
            return cast(
                so.Query,  # type: ignore[type-arg]  # SQLAlchemy2.0 - so.Query[Any]
                m.__query_cls__(mapper, session),  # type: ignore[union-attr]
            )
        except AttributeError:
            pass

    return so.Query(mapper, session)  # type: ignore[arg-type]


Session = so.sessionmaker(query_cls=_get_query_cls)

current_session = so.scoped_session(Session)
