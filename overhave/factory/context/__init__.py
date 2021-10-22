# flake8: noqa
from typing import TypeVar

from .admin_context import OverhaveAdminContext
from .emulation_context import OverhaveEmulationContext
from .publication_context import OverhavePublicationContext
from .synchronizer_context import OverhaveSynchronizerContext
from .test_execution_context import OverhaveTestExecutionContext

TApplicationContext = TypeVar(
    "TApplicationContext",
    OverhaveAdminContext,
    OverhaveTestExecutionContext,
    OverhavePublicationContext,
    OverhaveEmulationContext,
    OverhaveSynchronizerContext,
)
