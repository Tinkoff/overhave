import logging
from operator import attrgetter
from typing import Any, cast

from _pytest.fixtures import FixtureDef
from _pytest.main import Session

from overhave.entities import StepPrefixesModel
from overhave.storage import FeatureTypeName
from overhave.test_execution.objects import BddStepModel, is_public_step
from overhave.test_execution.settings import OverhaveStepCollectorSettings

_PYTESTBDD_FIXTURE_MARK = "pytestbdd_"
_PYTESTBDD_FIXTURE_TRACE_MARK = "_trace"

logger = logging.getLogger(__name__)


class BaseStepCollectorException(Exception):
    """Base exception for :class:`StepCollector`."""


class BddStepWithoutDocsError(BaseStepCollectorException):
    """Error for situation when pytest_bdd steps declared without docstring."""


class StepCollector:
    """Class for `pytest-bdd` steps dynamic collection."""

    def __init__(self, settings: OverhaveStepCollectorSettings, step_prefixes: StepPrefixesModel | None) -> None:
        self._settings = settings
        self._step_prefixes = step_prefixes
        self._steps: dict[FeatureTypeName, list[BddStepModel]] = {}

    def _is_bdd_step(self, fixture: FixtureDef[Any]) -> bool:
        is_bdd_step = (
            isinstance(fixture.argname, str)
            and fixture.argname.startswith(_PYTESTBDD_FIXTURE_MARK)
            and not fixture.argname.endswith(_PYTESTBDD_FIXTURE_TRACE_MARK)
        )
        logger.debug("Fixture: %s - is_bdd_step=%s", fixture.argname, is_bdd_step)
        if not is_bdd_step:
            return False
        step_func = fixture.func._pytest_bdd_step_context.step_func  # type: ignore[union-attr]
        if self._settings.hide_non_public_steps and not is_public_step(step_func):
            logger.debug("Step func: %s is not public! Mark as non bdd step.", step_func)
            return False
        if not isinstance(step_func.__doc__, str):
            raise BddStepWithoutDocsError(
                f"Fixture {fixture} does not have description! Please, set it via docstrings."
            )
        return True

    def _get_pytestbdd_step_fixtures(self, session: Session) -> tuple[FixtureDef[Any], ...]:
        return cast(
            tuple[FixtureDef[Any], ...],
            sorted(
                (
                    fx
                    for fx_list in session._fixturemanager._arg2fixturedefs.values()
                    for fx in fx_list
                    if self._is_bdd_step(fx)
                ),
                key=attrgetter("func._pytest_bdd_step_context.type"),
                reverse=True,
            ),
        )

    def _compile_full_step_name(self, fixture_name: str, step_type: str) -> str:
        prefix = step_type.title()
        if self._step_prefixes is not None:
            prefix = self._step_prefixes.model_dump()[step_type.upper()].strip()
        return f"{prefix} {fixture_name}"

    def _compile_step_models(self, steps: tuple[FixtureDef[Any], ...]) -> list[BddStepModel]:
        return [
            BddStepModel(
                type=f.func._pytest_bdd_step_context.type,  # type: ignore
                name=self._compile_full_step_name(
                    fixture_name=f.func._pytest_bdd_step_context.parser.name,  # type: ignore
                    step_type=f.func._pytest_bdd_step_context.type,  # type: ignore
                ),
                doc=f.func._pytest_bdd_step_context.step_func.__doc__,  # type: ignore
            )
            for f in steps
        ]

    def collect_steps(self, session: Session, feature_type: FeatureTypeName) -> None:
        logger.debug("Collecting steps for feature_type=%s...", feature_type)
        step_fixtures = self._get_pytestbdd_step_fixtures(session)
        bdd_steps = self._compile_step_models(step_fixtures)
        if bdd_steps:
            logger.debug("Loaded steps dict:\n%s", bdd_steps)
        else:
            logger.warning("Feature type '%s' does not have any pytest_bdd steps!", feature_type)
        self._steps[feature_type] = bdd_steps

    def get_steps(self, feature_type: FeatureTypeName) -> list[BddStepModel] | None:
        return self._steps.get(feature_type)
