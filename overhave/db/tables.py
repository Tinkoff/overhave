from __future__ import annotations

import datetime
from typing import Dict, List

import allure
import sqlalchemy as sa
import sqlalchemy_utils as su
from flask import url_for
from sqlalchemy import orm as so

from overhave.db.base import BaseTable, PrimaryKeyMixin, PrimaryKeyWithoutDateMixin
from overhave.db.statuses import DraftStatus, EmulationStatus, TestReportStatus, TestRunStatus
from overhave.db.users import UserRole


class FeatureType(BaseTable, PrimaryKeyWithoutDateMixin):
    """Feature types table."""

    name: str = sa.Column(sa.Text, unique=True, nullable=False, doc="Feature types choice")

    def __repr__(self) -> str:
        return self.name.upper()


class Tags(BaseTable, PrimaryKeyMixin):
    """Feature tags table."""

    value: str = sa.Column(sa.String(), nullable=False, unique=True, doc="Feature tags choice")
    created_by: str = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), nullable=False, doc="Author login")

    def __repr__(self) -> str:
        return self.value

    def __init__(self, value: str, created_by: str) -> None:
        self.value = value
        self.created_by = created_by


@su.generic_repr("id", "name", "last_edited_by")
class Feature(BaseTable, PrimaryKeyMixin):
    """Features table."""

    name: str = sa.Column(sa.String(), doc="Feature name", nullable=False, unique=True)
    author: str = sa.Column(
        sa.String(), sa.ForeignKey(UserRole.login), doc="Feature author login", nullable=False, index=True
    )
    type_id: int = sa.Column(sa.Integer(), sa.ForeignKey(FeatureType.id), nullable=False, doc="Feature types choice")
    file_path: str = sa.Column(sa.String(), doc="Feature file path", nullable=False, unique=True)
    task: List[str] | None = sa.Column(sa.ARRAY(sa.String()), doc="Feature tasks list", nullable=True)
    last_edited_by: str = sa.Column(sa.String(), doc="Last feature editor login", nullable=False)
    last_edited_at: datetime.datetime = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    released: bool = sa.Column(sa.Boolean, doc="Feature release state boolean", nullable=False, default=False)
    severity: allure.severity_level = sa.Column(
        sa.Enum(allure.severity_level),
        nullable=False,
        default=allure.severity_level.NORMAL,
        doc="Feature severity choice",
    )

    feature_type: so.Mapped[FeatureType] = so.relationship(FeatureType, uselist=False)
    feature_tags: so.Mapped[List[Tags]] = so.relationship(
        Tags, uselist=True, order_by=Tags.value, secondary="feature_tags_association_table"
    )

    def __init__(
        self,
        name: str,
        author: str,
        type_id: int,
        file_path: str,
        task: List[str] | None,
        severity: allure.severity_level,
        last_edited_at: datetime.datetime,
    ) -> None:
        self.name = name
        self.author = author
        self.type_id = type_id
        self.file_path = file_path
        self.task = task
        self.last_edited_by = author
        self.severity = severity
        self.last_edited_at = last_edited_at


class FeatureTagsAssociationTable(BaseTable, PrimaryKeyWithoutDateMixin):
    """Association table between features and tags."""

    extend_existing = True

    tags_id: int = sa.Column(sa.Integer(), sa.ForeignKey(Tags.id))
    feature_id: int = sa.Column(sa.Integer(), sa.ForeignKey(Feature.id))


@su.generic_repr("feature_id")
class Scenario(BaseTable, PrimaryKeyMixin):
    """Scenarios table."""

    feature_id: int = sa.Column(sa.Integer(), sa.ForeignKey(Feature.id), nullable=False, unique=True)
    text: str | None = sa.Column(sa.Text(), doc="Text storage for scenarios in feature")

    feature: so.Mapped[Feature] = so.relationship(
        Feature, uselist=False, backref=so.backref("scenario", cascade="all, delete-orphan")
    )


class TestRun(BaseTable, PrimaryKeyMixin):
    """Test runs table."""

    __test__ = False

    scenario_id: int = sa.Column(sa.Integer(), sa.ForeignKey(Scenario.id), nullable=False, index=True)
    name: str = sa.Column(sa.String(), nullable=False)
    start: datetime.datetime | None = sa.Column(sa.DateTime(timezone=True), doc="Test start time")
    end: datetime.datetime | None = sa.Column(sa.DateTime(timezone=True), doc="Test finish time")
    status: TestRunStatus = sa.Column(sa.Enum(TestRunStatus), doc="Current test status", nullable=False)
    report_status: TestReportStatus = sa.Column(
        sa.Enum(TestReportStatus), doc="Report generation result", nullable=False
    )
    executed_by: str = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Test executor login", nullable=False)
    report: str | None = sa.Column(sa.String(), doc="Relative report URL")
    traceback: str | None = sa.Column(sa.Text(), doc="Text storage for error traceback")

    scenario: so.Mapped[Scenario] = so.relationship(
        Scenario, uselist=False, backref=so.backref("test_runs", cascade="all, delete-orphan")
    )


class DraftQuery(so.Query):  # type: ignore[type-arg]  # SQLAlchemy2.0 - so.Query[Any]
    """Scenario versions table."""

    def as_unique(self, test_run_id: int, published_by: str, status: DraftStatus) -> Draft:
        with self.session.no_autoflush:
            run = self.session.get(TestRun, test_run_id)
            if run is None:
                raise RuntimeError(f"Unknown test_run_id={test_run_id}!")
            if run.scenario.text is None:
                raise RuntimeError(f"Scenario with id={run.scenario} has empty text!")
            draft = (
                self.session.query(Draft)
                .filter(Draft.test_run_id == run.id, Draft.text == run.scenario.text)
                .one_or_none()
            )
        if draft is not None:
            return draft
        return Draft(
            feature_id=run.scenario.feature_id,
            test_run_id=test_run_id,
            text=run.scenario.text,
            published_by=published_by,
            status=status,
        )


class Draft(BaseTable, PrimaryKeyMixin):
    """Scenario versions table."""

    __query_cls__ = DraftQuery

    feature_id: int = sa.Column(sa.Integer(), sa.ForeignKey(Feature.id), nullable=False, index=True)
    test_run_id: int = sa.Column(sa.Integer(), sa.ForeignKey(TestRun.id), nullable=False)
    text: str | None = sa.Column(sa.Text(), doc="Released scenario text")
    pr_url: str | None = sa.Column(sa.String(), doc="Absolute pull-request URL")
    published_by: str = sa.Column(
        sa.String(), sa.ForeignKey(UserRole.login), doc="Draft publisher login", nullable=False
    )
    published_at: datetime.datetime | None = sa.Column(sa.DateTime(timezone=True), doc="Publication time")
    traceback: str | None = sa.Column(sa.Text(), doc="Text storage for error traceback")
    status: DraftStatus = sa.Column(sa.Enum(DraftStatus), doc="Version publishing status", nullable=False)

    feature: so.Mapped[Feature] = so.relationship(
        Feature, uselist=False, backref=so.backref("versions", cascade="all, delete-orphan")
    )

    __table_args__ = (sa.UniqueConstraint(test_run_id),)

    def __html__(self) -> str:
        return f'<a href="{url_for("draft.details_view", id=self.id)}">Draft: {self.id}</a>'

    def __init__(self, feature_id: int, test_run_id: int, text: str, published_by: str, status: DraftStatus) -> None:
        self.feature_id = feature_id
        self.test_run_id = test_run_id
        self.text = text
        self.published_by = published_by
        self.status = status


@su.generic_repr("id", "name", "created_by")
class TestUser(BaseTable, PrimaryKeyMixin):
    """Test users table."""

    __test__ = False

    key: str = sa.Column(sa.String(), nullable=False, unique=True, doc="Unique user key")
    name: str = sa.Column(sa.String(), nullable=False, unique=True, doc="Informational user name")
    feature_type_id: int = sa.Column(
        sa.Integer(), sa.ForeignKey(FeatureType.id), nullable=False, doc="Feature types choice"
    )
    specification: Dict[str, str | None] = sa.Column(sa.JSON(none_as_null=True))
    created_by: str = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Author login", nullable=False)
    allow_update: bool = sa.Column(sa.Boolean(), doc="User updating allowance", nullable=False, default=False)
    changed_at: datetime.datetime = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())

    feature_type: so.Mapped[FeatureType] = so.relationship(FeatureType, uselist=False)


class Emulation(BaseTable, PrimaryKeyMixin):
    """Emulation templates table."""

    name: str = sa.Column(sa.String(), nullable=False, unique=True)
    test_user_id: int = sa.Column(sa.Integer(), sa.ForeignKey(TestUser.id), nullable=False, doc="Test user ID")
    command: str = sa.Column(sa.String(), nullable=False, doc="Command for emulator's execution")
    created_by: str = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Author login", nullable=False)

    test_user: so.Mapped[TestUser] = so.relationship(
        TestUser, uselist=False, backref=so.backref("emulations", cascade="all, delete-orphan")
    )


class EmulationRun(BaseTable, PrimaryKeyMixin):
    """Emulation runs table."""

    emulation_id: int = sa.Column(sa.Integer(), sa.ForeignKey(Emulation.id), nullable=False, index=True)
    status: EmulationStatus = sa.Column(sa.Enum(EmulationStatus), doc="Current emulation status", nullable=False)
    changed_at: datetime.datetime = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    port: int | None = sa.Column(sa.Integer(), doc="Port for emulation")
    traceback: str | None = sa.Column(sa.Text(), doc="Text storage for error traceback")
    initiated_by: str = sa.Column(
        sa.String(), sa.ForeignKey(UserRole.login), doc="Initiator of start emulation", nullable=False
    )

    emulation: so.Mapped[Emulation] = so.relationship(
        Emulation, uselist=False, backref=so.backref("emulation_runs", cascade="all, delete-orphan")
    )

    def __init__(self, emulation_id: int, initiated_by: str) -> None:
        self.emulation_id = emulation_id
        self.status = EmulationStatus.CREATED
        self.initiated_by = initiated_by
