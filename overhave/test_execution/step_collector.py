import logging
from operator import attrgetter
from typing import Any, Dict, List, Optional, Tuple, cast

from _pytest.fixtures import FixtureDef
from _pytest.main import Session

from overhave.entities import FeatureTypeName, StepPrefixesModel
from overhave.test_execution.objects import BddStepModel

_PYTESTBDD_FIXTURE_MARK = "pytestbdd_"
_PYTESTBDD_FIXTURE_TRACE_MARK = "_trace"

logger = logging.getLogger(__name__)


class BaseStepCollectorException(Exception):
    """Base exception for :class:`StepCollector`."""


class BddStepWithoutDocsError(BaseStepCollectorException):
    """Error for situation when pytest_bdd steps declared without docstring."""


class StepCollector:
    """Class for `pytest-bdd` steps dynamic collection."""

    def __init__(self, step_prefixes: Optional[StepPrefixesModel]) -> None:
        self._step_prefixes = step_prefixes
        self._steps: Dict[FeatureTypeName, List[BddStepModel]] = {}

    @staticmethod
    def _is_bdd_step(fixture: FixtureDef[Any]) -> bool:
        is_bdd_step = (
            isinstance(fixture.argname, str)
            and fixture.argname.startswith(_PYTESTBDD_FIXTURE_MARK)
            and not fixture.argname.endswith(_PYTESTBDD_FIXTURE_TRACE_MARK)
        )
        logger.debug("Fixture: %s - is_bdd_step=%s", fixture.argname, is_bdd_step)
        if is_bdd_step and not isinstance(fixture.func.__doc__, str):
            raise BddStepWithoutDocsError(
                f"Fixture {fixture} does not have description! Please, set it via docstrings."
            )
        return is_bdd_step

    @classmethod
    def _get_pytestbdd_step_fixtures(cls, session: Session) -> Tuple[FixtureDef[Any]]:
        return cast(
            Tuple[FixtureDef[Any]],
            sorted(
                (
                    fx
                    for fx_list in session._fixturemanager._arg2fixturedefs.values()
                    for fx in fx_list
                    if cls._is_bdd_step(fx)
                ),
                key=attrgetter("func.step_type"),
                reverse=True,
            ),
        )

    def _compile_full_step_name(self, fixture_name: str, step_type: str) -> str:
        prefix = step_type.title()
        if self._step_prefixes is not None:
            prefix = self._step_prefixes.dict()[step_type.upper()].strip()
        return f"{prefix} {fixture_name}"

    def _compile_step_models(self, steps: Tuple[FixtureDef[Any]]) -> List[BddStepModel]:
        return [
            BddStepModel(
                type=f.func.step_type,  # type: ignore
                name=self._compile_full_step_name(
                    fixture_name=f.func.parser.name,  # type: ignore
                    step_type=f.func.step_type,  # type: ignore
                ),
                doc=f.func.__doc__,
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

    def get_steps(self, feature_type: FeatureTypeName) -> Optional[List[BddStepModel]]:
        return self._steps.get(feature_type)
