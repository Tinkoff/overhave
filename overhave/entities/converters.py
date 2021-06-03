from datetime import datetime
from typing import List, Optional

from pydantic.main import BaseModel
from pydantic.types import SecretStr
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from overhave.db import (
    Draft,
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
from overhave.entities.feature import FeatureTypeName


class SystemUserModel(sqlalchemy_to_pydantic(UserRole)):  # type: ignore
    """ Model for :class:`UserRole`. """

    login: str
    password: SecretStr
    role: Role


class FeatureTypeModel(sqlalchemy_to_pydantic(FeatureType)):  # type: ignore
    """ Model for :class:`FeatureType` row. """

    name: FeatureTypeName


class TagsTypeModel(sqlalchemy_to_pydantic(Tags)):  # type: ignore
    """ Model for :class:`Tags` row. """

    value: str


class FeatureModel(sqlalchemy_to_pydantic(Feature)):  # type: ignore
    """ Model for :class:`Feature` row. """

    id: int
    name: str
    author: str
    feature_type: FeatureTypeModel
    last_edited_by: str
    task: List[str]
    feature_tags: List[TagsTypeModel]
    file_path: str


class ScenarioModel(sqlalchemy_to_pydantic(Scenario)):  # type: ignore
    """ Model for :class:`Scenario` row. """

    id: int
    text: str
    feature_id: int


class TestRunModel(sqlalchemy_to_pydantic(TestRun)):  # type: ignore
    """ Model for :class:`TestRun` row. """

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
    """ Model for :class:`Draft` row. """

    id: int
    feature_id: int
    test_run_id: int
    pr_url: Optional[str]
    published_by: str
    published_at: Optional[datetime]


class TestExecutorContext(BaseModel):
    """ Context model for test execution. """

    __test__ = False

    feature: FeatureModel
    scenario: ScenarioModel
    test_run: TestRunModel


class PublisherContext(TestExecutorContext):
    """ Context model for version publishing. """

    draft: DraftModel
    target_branch: str


class TestUserModel(sqlalchemy_to_pydantic(TestUser)):  # type: ignore
    """ Model for :class:`TestUser` row. """

    feature_type: FeatureTypeModel


class EmulationModel(sqlalchemy_to_pydantic(Emulation)):  # type: ignore
    """ Model for :class:`Emulation` row. """

    test_user: TestUserModel


class EmulationRunModel(sqlalchemy_to_pydantic(EmulationRun)):  # type: ignore
    """ Model for :class:`EmulationRun` row. """

    emulation: EmulationModel
