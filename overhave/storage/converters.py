from datetime import datetime
from typing import NewType

import allure
from pydantic.main import BaseModel
from pydantic.types import SecretStr

from overhave import db
from overhave.db import DraftStatus, Role, TestReportStatus, TestRunStatus

FeatureTypeName = NewType("FeatureTypeName", str)
TestUserSpecification = NewType("TestUserSpecification", dict[str, str | None])


class _SqlAlchemyOrmModel(BaseModel):
    """:class:`BaseModel` with enabled `orm_mode`."""

    class Config:
        from_attributes = True


class SystemUserModel(_SqlAlchemyOrmModel):
    """Model for :class:`UserRole`."""

    id: int
    login: str
    password: SecretStr | None
    role: Role

    def get_id(self) -> int:
        return self.id

    def __unicode__(self) -> str:
        return self.login


class FeatureTypeModel(_SqlAlchemyOrmModel):
    """Model for :class:`FeatureType` row."""

    id: int
    name: FeatureTypeName


class TagModel(_SqlAlchemyOrmModel):
    """Model for :class:`Tags` row."""

    id: int
    value: str
    created_by: str


class FeatureModel(_SqlAlchemyOrmModel):
    """Model for :class:`Feature` row."""

    id: int
    created_at: datetime
    name: str
    author: str
    type_id: int
    last_edited_by: str
    last_edited_at: datetime
    task: list[str]
    file_path: str
    released: bool
    severity: allure.severity_level

    feature_type: FeatureTypeModel
    feature_tags: list[TagModel]


class ScenarioModel(_SqlAlchemyOrmModel):
    """Model for :class:`Scenario` row."""

    id: int
    text: str
    feature_id: int


class TestRunModel(_SqlAlchemyOrmModel):
    """Model for :class:`TestRun` row."""

    __test__ = False

    id: int
    created_at: datetime
    name: str
    executed_by: str
    start: datetime | None
    end: datetime | None
    status: TestRunStatus
    report_status: TestReportStatus
    report: str | None
    traceback: str | None
    scenario_id: int


class DraftModel(_SqlAlchemyOrmModel):
    """Model for :class:`Draft` row."""

    id: int
    feature_id: int
    test_run_id: int
    pr_url: str | None
    published_by: str
    published_at: datetime | None
    traceback: str | None
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


class TestUserModel(_SqlAlchemyOrmModel):
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


class EmulationModel(_SqlAlchemyOrmModel):
    """Model for :class:`Emulation` row."""

    id: int
    command: str
    test_user: TestUserModel


class EmulationRunModel(_SqlAlchemyOrmModel):
    """Model for :class:`EmulationRun` row."""

    id: int
    emulation_id: int
    changed_at: datetime
    status: db.EmulationStatus
    port: int | None
    initiated_by: str
    emulation: EmulationModel
