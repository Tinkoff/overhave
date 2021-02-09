import enum
import logging
from functools import cached_property
from typing import Optional, cast
from unittest.mock import MagicMock

import allure
from allure_commons._allure import StepContext

from overhave.base_settings import OverhaveLoggingSettings


class _WrapperPosition(str, enum.Enum):
    ABOVE = "above"
    BELOW = "below"


class StepContextNotDefinedError(Exception):
    """ Exception for situation with calling for self._step, when StepContext has not been defined. """


class StepContextRunner:
    """ Class for Allure StepContext wrapping during pytest-bdd step execution. """

    def __init__(self, logging_settings: OverhaveLoggingSettings) -> None:
        self._logging_settings = logging_settings

        self._step: Optional[StepContext] = None

    def set_title(self, title: str) -> None:
        self._step = allure.step(title)

    @cached_property
    def _defined_step(self) -> StepContext:
        if isinstance(self._step, StepContext):
            return self._step
        raise StepContextNotDefinedError("Current Allure step not defined!")

    @cached_property
    def _logger(self) -> logging.Logger:
        if self._logging_settings.step_context_logs:
            return logging.getLogger("overhave")
        return cast(logging.Logger, MagicMock())

    def _log_step_state(self, state: str, wrapper_position: _WrapperPosition, symbol: str) -> None:
        description = f"{state.title()} step '{self._defined_step.title}'"
        wrapper = symbol * (len(description) - 2)
        if wrapper_position is _WrapperPosition.ABOVE:
            args = (wrapper, description)
        else:
            args = (description, wrapper)
        self._logger.info("")
        for arg in args:
            self._logger.info("%s", arg)
        self._logger.info("")

    def start(self) -> None:
        self._defined_step.__enter__()
        self._log_step_state(state="started", wrapper_position=_WrapperPosition.ABOVE, symbol="*")

    def stop(self, exception: Optional[BaseException]) -> None:
        if isinstance(exception, BaseException):
            self._log_step_state(state="failed", wrapper_position=_WrapperPosition.BELOW, symbol="!")
            self._defined_step.__exit__(exc_type=type(exception), exc_val=exception, exc_tb=exception.__traceback__)
        else:
            self._log_step_state(state="finished", wrapper_position=_WrapperPosition.BELOW, symbol="-")
            self._defined_step.__exit__(exc_type=None, exc_val=None, exc_tb=None)
