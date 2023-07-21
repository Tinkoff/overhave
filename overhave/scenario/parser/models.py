from dataclasses import dataclass, field
from datetime import datetime

import allure

from overhave.storage import FeatureTypeName


@dataclass
class FeatureInfo:
    """Model for feature info keeping."""

    id: int | None = None
    name: str | None = None
    type: FeatureTypeName | None = None
    tags: list[str] | None = None
    severity: allure.severity_level | None = None
    author: str | None = None
    last_edited_by: str | None = None
    last_edited_at: datetime | None = None
    tasks: list[str] | None = None
    scenarios: str | None = None


@dataclass
class StrictFeatureInfo:
    """Model for feature info keeping with strict presence of fields."""

    id: int
    name: str
    type: FeatureTypeName
    author: str
    last_edited_by: str
    last_edited_at: datetime
    scenarios: str

    tags: list[str] = field(default_factory=list)
    severity: allure.severity_level = allure.severity_level.NORMAL
    tasks: list[str] = field(default_factory=list)
