import logging
from types import FunctionType
from typing import Any, Callable, Sequence, Type, Union

from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup

from overhave import db

logger = logging.getLogger(__name__)


def _default_formatter_result(
    model: db.BaseTable, name: str, supported_models: Sequence[Type[db.BaseTable]]
) -> Union[Markup, Any]:
    value = getattr(model, name, None)
    if value is None:
        return Markup("")
    if not isinstance(model, tuple(supported_models)):
        return Markup(value)
    return value


def safe_formatter(type: Type[object], supported_models: Sequence[Type[db.BaseTable]]):  # type: ignore  # noqa: A002
    def decorator(func: FunctionType) -> Callable[[ModelView, Any, db.BaseTable, str], Union[Markup, Any]]:
        def wrapper(view: ModelView, context: Any, model: db.BaseTable, name: str) -> Union[Markup, Any]:
            logger.debug("Wrapping function '%s'...", func.__name__)
            result = _default_formatter_result(model=model, name=name, supported_models=supported_models)
            logger.debug("Default formatter result: '%s'", result)
            if not isinstance(result, Markup) and isinstance(result, type):
                result = func(view, context, model, result)
                logger.debug("'%s' result: '%s'", func.__name__, result)
            return result

        return wrapper

    return decorator
