from datetime import datetime

import allure
from pydantic import BaseModel

from overhave.storage import FeatureTypeName


class FeatureInfo(BaseModel):
    """Model for feature info keeping."""

    id: int | None
    name: str | None
    type: FeatureTypeName | None
    tags: list[str] | None
    severity: allure.severity_level | None
    author: str | None
    last_edited_by: str | None
    last_edited_at: datetime | None
    tasks: list[str] | None
    scenarios: str | None


class StrictFeatureInfo(BaseModel):
    """Model for feature info keeping with strict presence of fields."""

    id: int
    name: str
    type: FeatureTypeName
    tags: list[str] = []
    severity: allure.severity_level = allure.severity_level.NORMAL
    author: str
    last_edited_by: str
    last_edited_at: datetime
    tasks: list[str] = []
    scenarios: str
