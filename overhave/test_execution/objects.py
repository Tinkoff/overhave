import re
from typing import NewType

from pydantic import BaseModel, validator
from pytest_bdd.types import STEP_TYPES

StepTypeName = NewType("StepTypeName", str)


class BddStepModel(BaseModel):
    """Model for pytest_bdd step in Overhave."""

    type: StepTypeName
    name: str
    doc: str

    @validator("type")
    def validate_type(cls, v: str) -> StepTypeName:
        if v not in STEP_TYPES:
            raise ValueError
        return StepTypeName(v)

    @property
    def html_doc(self) -> str:
        return re.sub(r"\n\s{4}", "\n", self.doc).strip("\n ")
