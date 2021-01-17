from __future__ import annotations

import datetime
import logging
import re
from typing import List, Type

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapper
from sqlalchemy.orm import Session as SessionClass
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.query import Query

from overhave.db.types import INT_TYPE

logger = logging.getLogger(__name__)

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


@as_declarative(metadata=metadata)
class Base:
    """ Base table class with __tablename__. """

    @declared_attr
    def __tablename__(cls) -> str:
        return _classname_to_tablename(cls.__name__)  # type: ignore


class PrimaryKeyWithoutDateMixin:
    """ Table mixin with declared attribute `id`. """

    @declared_attr
    def id(cls) -> sa.Column[int]:
        return sa.Column(f'{cls.__tablename__}_id', INT_TYPE, primary_key=True)  # type: ignore


class PrimaryKeyMixin(PrimaryKeyWithoutDateMixin):
    """ Table mixin with `id` and `created_at` declared attributes. """

    @declared_attr
    def created_at(cls) -> sa.Column[datetime.datetime]:
        return sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now())


def _get_query_cls(mapper: Type[Base], session: SessionClass) -> Query:
    if mapper:
        m = mapper
        if isinstance(m, tuple):
            m = mapper[0]
        if isinstance(m, Mapper):
            m = m.entity

        try:
            return m.__query_cls__(mapper, session)  # type: ignore
        except AttributeError:
            pass

    return Query(mapper, session)


def _classname_to_tablename(name: str) -> str:
    result: List[str] = []

    last_index = 0
    for match in re.finditer(r'(?P<abbreviation>[A-Z]+(?![a-z\d]))|(?P<word>[A-Z][a-z]*)|(?P<digit>\d+)', name):
        if match.start() != last_index:
            raise ValueError(f'Could not translate class name "{name}" to table name')

        last_index = match.end()
        result.append(match.group().lower())

    return '_'.join(result)


Session = sessionmaker(query_cls=_get_query_cls)

current_session = scoped_session(Session)
