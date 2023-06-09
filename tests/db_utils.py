import ctypes
import logging
import operator
import threading
from contextlib import contextmanager
from typing import Any, Callable, Iterable, Iterator

import sqlalchemy as sa
import sqlalchemy.orm as so
from _pytest.fixtures import FixtureRequest
from sqlalchemy import event

from overhave import db
from overhave.db import create_session

BEFORE_CURSOR_EXECUTE_EVENT_NAME = "before_cursor_execute"
AFTER_CURSOR_EXECUTE_EVENT_NAME = "after_cursor_execute"


class _ThreadLocals(threading.local):
    need_sql_counter: bool = False
    fixture_request: FixtureRequest | None = None

    def get_fixture_request(self) -> FixtureRequest:
        if self.fixture_request is None:
            raise RuntimeError("fixture_request has not been set!")
        return self.fixture_request


THREAD_LOCALS = _ThreadLocals()


class SQLCounter:
    """Class for SQL queries count in tests."""

    def __init__(
        self,
    ) -> None:
        self._counter = 0

    def increase_counter(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=W0613
        self._counter += 1

    @property
    def counter(self) -> int:
        return self._counter

    def __enter__(self) -> "SQLCounter":
        event.listen(sa.Engine, AFTER_CURSOR_EXECUTE_EVENT_NAME, self.increase_counter)
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        event.remove(sa.Engine, AFTER_CURSOR_EXECUTE_EVENT_NAME, self.increase_counter)


def _get_py_obj_value(obj_id: int) -> ctypes.py_object:  # type: ignore[type-arg]
    return ctypes.cast(obj_id, ctypes.py_object).value  # type: ignore[no-any-return]


def _get_py_objects(obj_ids: list[int | tuple[int, int]]) -> Iterable[ctypes.py_object]:  # type: ignore
    for element in obj_ids:
        if isinstance(element, tuple):
            for obj_id in element:
                yield _get_py_obj_value(obj_id)
        else:
            yield _get_py_obj_value(element)


def validate_db_session(*args: Any, **kwargs: Any) -> None:
    if not THREAD_LOCALS.need_sql_counter:
        return

    py_obj_ids: list[int | tuple[int, int]] = [
        obj_ids
        for _engine, listen_for, obj_ids in event.registry._key_to_collection
        if listen_for == AFTER_CURSOR_EXECUTE_EVENT_NAME
    ]

    for py_obj in _get_py_objects(py_obj_ids):
        if SQLCounter.__name__ in py_obj.__qualname__:  # type: ignore
            break
    else:
        raise RuntimeError(
            f"Using db.{create_session.__name__}() without {SQLCounter.__name__}! "
            f"Please, add `with {count_queries.__name__}(expected_count=n):` to your test"
        )


@contextmanager
def count_queries(
    expected_count: int,
    comparator: Callable[[int, int], bool] = operator.eq,
) -> Iterator[None]:
    request = THREAD_LOCALS.get_fixture_request()
    log_capture = request.getfixturevalue("caplog")
    log_capture._item = request.node
    log_capture = log_capture.at_level(logging.INFO, logger="sqlalchemy.engine")
    with SQLCounter() as sql_counter:
        with log_capture:
            yield
    assert comparator(sql_counter.counter, expected_count), (sql_counter.counter, expected_count)


@contextmanager
def create_test_session(expire_on_commit: bool = True, **kwargs: Any) -> Iterator[so.Session]:
    """Provide a transactional scope around a series of operations."""
    initial_state = THREAD_LOCALS.need_sql_counter
    THREAD_LOCALS.need_sql_counter = False
    new_session = db.base.Session(expire_on_commit=expire_on_commit, bind=db.metadata.engine, **kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        THREAD_LOCALS.need_sql_counter = initial_state
        new_session.close()
