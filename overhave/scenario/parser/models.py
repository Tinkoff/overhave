from datetime import datetime
from typing import List, Optional

import allure
from pydantic import BaseModel

from overhave.storage import FeatureTypeName


class FeatureInfo(BaseModel):
    """Model for feature info keeping."""

    id: Optional[int]
    name: Optional[str]
    type: Optional[FeatureTypeName]
    tags: Optional[List[str]]
    severity: Optional[allure.severity_level]
    author: Optional[str]
    last_edited_by: Optional[str]
    last_edited_at: Optional[datetime]
    tasks: Optional[List[str]]
    scenarios: Optional[str]


class StrictFeatureInfo(BaseModel):
    """Model for feature info keeping with strict presence of fields."""

    id: int
    name: str
    type: FeatureTypeName
    tags: List[str] = []
    severity: allure.severity_level = allure.severity_level.NORMAL
    author: str
    last_edited_by: str
    last_edited_at: datetime
    tasks: List[str] = []
    scenarios: str
