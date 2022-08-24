from datetime import datetime
from typing import List, NewType, Optional

import allure
from pydantic.main import BaseModel
from pydantic.types import SecretStr
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from overhave.db import (
    Draft,
    DraftStatus,
    Emulation,
    EmulationRun,
    Feature,
    FeatureType,
    Role,
    Scenario,
    Tags,
    TestReportStatus,
    TestRun,
    TestRunStatus,
    TestUser,
    UserRole,
)

FeatureTypeName = NewType("FeatureTypeName", str)
TestUserSpecification = NewType("TestUserSpecification", dict[str, str | None])


class SystemUserModel(sqlalchemy_to_pydantic(UserRole)):  # type: ignore
    """Model for :class:`UserRole`."""

    id: int
    login: str
    password: Optional[SecretStr]
    role: Role

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> int:
        return self.id

    def __unicode__(self) -> str:
        return self.login


class FeatureTypeModel(sqlalchemy_to_pydantic(FeatureType)):  # type: ignore
    """Model for :class:`FeatureType` row."""

    id: int
    name: FeatureTypeName


class TagModel(sqlalchemy_to_pydantic(Tags)):  # type: ignore
    """Model for :class:`Tags` row."""

    id: int
    value: str
    created_by: str


class FeatureModel(sqlalchemy_to_pydantic(Feature)):  # type: ignore
    """Model for :class:`Feature` row."""

    id: int
    name: str
    author: str
    type_id: int
    last_edited_by: str
    last_edited_at: datetime
    task: List[str]
    file_path: str
    released: bool
    severity: allure.severity_level

    feature_type: FeatureTypeModel
    feature_tags: List[TagModel]


class ScenarioModel(sqlalchemy_to_pydantic(Scenario)):  # type: ignore
    """Model for :class:`Scenario` row."""

    id: int
    text: str
    feature_id: int


class TestRunModel(sqlalchemy_to_pydantic(TestRun)):  # type: ignore
    """Model for :class:`TestRun` row."""

    __test__ = False

    id: int
    created_at: datetime
    name: str
    executed_by: str
    start: Optional[datetime]
    end: Optional[datetime]
    status: TestRunStatus
    report_status: TestReportStatus
    report: Optional[str]
    traceback: Optional[str]
    scenario_id: int


class DraftModel(sqlalchemy_to_pydantic(Draft)):  # type: ignore
    """Model for :class:`Draft` row."""

    id: int
    feature_id: int
    test_run_id: int
    pr_url: Optional[str]
    published_by: str
    published_at: Optional[datetime]
    traceback: Optional[str]
    status: DraftStatus


class TestExecutorContext(BaseModel):
    """Context model for test execution."""

    __test__ = False

    feature: FeatureModel
    scenario: ScenarioModel
    test_run: TestRunModel


class PublisherContext(TestExecutorContext):
    """Context model for version publishing."""

    draft: DraftModel
    target_branch: str


class TestUserModel(sqlalchemy_to_pydantic(TestUser)):  # type: ignore
    """Model for :class:`TestUser` row."""

    __test__ = False

    id: int
    created_at: datetime
    key: str
    name: str
    created_by: str
    specification: TestUserSpecification
    feature_type_id: int
    feature_type: FeatureTypeModel
    allow_update: bool
    changed_at: datetime


class EmulationModel(sqlalchemy_to_pydantic(Emulation)):  # type: ignore
    """Model for :class:`Emulation` row."""

    test_user: TestUserModel


class EmulationRunModel(sqlalchemy_to_pydantic(EmulationRun)):  # type: ignore
    """Model for :class:`EmulationRun` row."""

    changed_at: datetime
    emulation: EmulationModel
