from operator import attrgetter
from typing import Any, Dict, List, Optional, Tuple, cast

from _pytest.fixtures import FixtureDef
from _pytest.main import Session
from pytest_bdd import types as default_types

from overhave.entities.language import StepPrefixesModel

_PYTESTBDD_FIXTURE_MARK = 'pytestbdd_'
_PYTESTBDD_FIXTURE_TRACE_MARK = '_trace'


class StepCollector:
    """ Class for `pytest-bdd` steps dynamic collection. """

    def __init__(self, step_prefixes: Optional[StepPrefixesModel]) -> None:
        self._step_prefixes = step_prefixes

    @staticmethod
    def _is_bdd_step(fixture: FixtureDef[Any]) -> bool:
        return (
            isinstance(fixture.argname, str)
            and fixture.argname.startswith(_PYTESTBDD_FIXTURE_MARK)
            and not fixture.argname.endswith(_PYTESTBDD_FIXTURE_TRACE_MARK)
        )

    @classmethod
    def get_pytestbdd_steps(cls, session: Session) -> Tuple[FixtureDef[Any]]:
        return cast(
            Tuple[FixtureDef[Any]],
            sorted(
                (
                    fx
                    for fx_list in session._fixturemanager._arg2fixturedefs.values()
                    for fx in fx_list
                    if cls._is_bdd_step(fx)
                ),
                key=attrgetter('func.step_type'),
                reverse=True,
            ),
        )

    def _compile_full_step_name(self, fixture_name: str, step_type: str) -> str:
        prefix = step_type.title()
        if self._step_prefixes is not None:
            prefix = self._step_prefixes.dict()[step_type.upper()].strip()
        return f"{prefix} {fixture_name}"

    def compile_steps_dict(self, steps: Tuple[FixtureDef[Any]]) -> Dict[str, List[str]]:
        return {
            step_type: [
                self._compile_full_step_name(fixture_name=f.func.parser.name, step_type=step_type)  # type: ignore
                for f in steps
                if f.func.step_type == step_type  # type: ignore
            ]
            for step_type in default_types.STEP_TYPES
        }
