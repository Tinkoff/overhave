from typing import List, Optional, Tuple, cast

from pydantic.main import BaseModel
from pytest_bdd import types as default_types
from pytest_bdd.parser import STEP_PREFIXES


class StepPrefixesModel(BaseModel):
    """ Base model for default STEP_PREFIXES extension. """

    FEATURE: str
    SCENARIO_OUTLINE: str
    SCENARIO: str
    BACKGROUND: str
    EXAMPLES: str
    EXAMPLES_VERTICAL: str
    GIVEN: str
    WHEN: str
    THEN: str
    AND: str
    BUT: str

    def extend_defaults(self) -> List[Tuple[str, Optional[str]]]:
        """ Extend default STEP_PREFIXES from pytest_bdd. """
        STEP_PREFIXES.append((self.FEATURE, default_types.FEATURE))
        STEP_PREFIXES.append((self.SCENARIO_OUTLINE, default_types.SCENARIO_OUTLINE))
        STEP_PREFIXES.append((self.SCENARIO, default_types.SCENARIO))
        STEP_PREFIXES.append((self.BACKGROUND, default_types.BACKGROUND))

        STEP_PREFIXES.append((self.EXAMPLES, default_types.EXAMPLES))
        STEP_PREFIXES.append((self.EXAMPLES_VERTICAL, default_types.EXAMPLES_VERTICAL))

        STEP_PREFIXES.append((self.GIVEN, default_types.GIVEN))
        STEP_PREFIXES.append((self.WHEN, default_types.WHEN))
        STEP_PREFIXES.append((self.THEN, default_types.THEN))

        STEP_PREFIXES.append((self.AND, None))
        STEP_PREFIXES.append((self.BUT, None))

        return cast(List[Tuple[str, Optional[str]]], STEP_PREFIXES)
