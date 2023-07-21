import re
from types import FunctionType
from typing import NewType

from pydantic import BaseModel, field_validator
from pytest_bdd.types import STEP_TYPES

StepTypeName = NewType("StepTypeName", str)
PUBLIC_STEP_ATTR_NAME = "_is_public_step"


class BddStepModel(BaseModel):
    """Model for pytest_bdd step in Overhave."""

    type: StepTypeName
    name: str
    doc: str

    @field_validator("type")
    def validate_type(cls, v: str) -> StepTypeName:
        if v not in STEP_TYPES:
            raise ValueError
        return StepTypeName(v)

    @property
    def html_doc(self) -> str:
        return re.sub(r"\n\s{4}", "\n", self.doc).strip("\n ")


def public_step(func: FunctionType) -> FunctionType:
    """
    Decorator for Overhave BDD steps, enables display of decorated step.

    Attention: `OverhaveStepCollectorSettings.hide_non_public_steps` setting should be `True`!
    """
    setattr(func, PUBLIC_STEP_ATTR_NAME, True)
    return func


def is_public_step(func: FunctionType) -> bool:
    return getattr(func, PUBLIC_STEP_ATTR_NAME, False)
