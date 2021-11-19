from __future__ import annotations

from typing import List, Optional, cast

import sqlalchemy as sa
import sqlalchemy_utils as su
from flask import url_for
from sqlalchemy import orm as so

from overhave.db.base import BaseTable, PrimaryKeyMixin, PrimaryKeyWithoutDateMixin, metadata
from overhave.db.statuses import DraftStatus, EmulationStatus, TestReportStatus, TestRunStatus
from overhave.db.users import UserRole

tags_association_table = sa.Table(
    "feature_tags",
    metadata,
    sa.Column("tags_id", sa.Integer(), sa.ForeignKey("tags.tags_id")),
    sa.Column("feature_id", sa.Integer(), sa.ForeignKey("feature.feature_id")),
    extend_existing=True,
)


class FeatureType(BaseTable, PrimaryKeyWithoutDateMixin):
    """Feature types table."""

    name = sa.Column(sa.Text, unique=True, nullable=False, doc="Feature types choice")

    def __repr__(self) -> str:
        return cast(str, self.name.upper())


class Tags(BaseTable, PrimaryKeyMixin):
    """Feature tags table."""

    value = sa.Column(sa.String(), nullable=False, doc="Feature tags choice", unique=True)
    created_by = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Author login", nullable=False)

    def __repr__(self) -> str:
        return cast(str, self.value)

    def __init__(self, value: str, created_by: str) -> None:
        self.value = value
        self.created_by = created_by


@su.generic_repr("name", "last_edited_by")
class Feature(BaseTable, PrimaryKeyMixin):
    """Features table."""

    name = sa.Column(sa.String(), doc="Feature name", nullable=False, unique=True)
    author = sa.Column(
        sa.String(), sa.ForeignKey(UserRole.login), doc="Feature author login", nullable=False, index=True
    )
    type_id = sa.Column(sa.Integer(), sa.ForeignKey(FeatureType.id), nullable=False, doc="Feature types choice")
    file_path = sa.Column(sa.String(), doc="Feature file path", nullable=False, unique=True)
    task = sa.Column(sa.ARRAY(sa.String()), doc="Feature tasks list", nullable=False)
    last_edited_by = sa.Column(sa.String(), doc="Last feature editor login", nullable=False)
    last_edited_at = sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now())
    released = sa.Column(sa.Boolean, doc="Feature release state boolean", nullable=False, default=False)

    feature_type = so.relationship(FeatureType)
    feature_tags = so.relationship(Tags, order_by=Tags.value, secondary=tags_association_table)

    def __init__(self, name: str, author: str, type_id: int, file_path: str, task: List[str]) -> None:
        self.name = name
        self.author = author
        self.type_id = type_id
        self.file_path = file_path
        self.task = task
        self.last_edited_by = author


@su.generic_repr("feature_id")
class Scenario(BaseTable, PrimaryKeyMixin):
    """Scenarios table."""

    feature_id = sa.Column(sa.Integer(), sa.ForeignKey(Feature.id), nullable=False, unique=True)
    text = sa.Column(sa.Text(), doc="Text storage for scenarios in feature")

    feature = so.relationship(Feature, backref=so.backref("scenario", cascade="all, delete-orphan"))


class TestRun(BaseTable, PrimaryKeyMixin):
    """Test runs table."""

    __test__ = False

    scenario_id = sa.Column(sa.Integer(), sa.ForeignKey(Scenario.id), nullable=False, index=True)
    name = sa.Column(sa.String(), nullable=False)
    start = sa.Column(sa.DateTime(timezone=True), doc="Test start time")
    end = sa.Column(sa.DateTime(timezone=True), doc="Test finish time")
    status = sa.Column(sa.Enum(TestRunStatus), doc="Current test status", nullable=False)
    report_status = sa.Column(sa.Enum(TestReportStatus), doc="Report generation result", nullable=False)
    executed_by = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Test executor login", nullable=False)
    report = sa.Column(sa.String(), doc="Relative report URL")
    traceback = sa.Column(sa.Text(), doc="Text storage for error traceback")

    scenario = so.relationship(Scenario, backref=so.backref("test_runs", cascade="all, delete-orphan"))


class DraftQuery(so.Query):
    """Scenario versions table."""

    def as_unique(self, test_run_id: int, published_by: str, status: DraftStatus) -> Draft:
        with self.session.no_autoflush:
            run = self.session.query(TestRun).get(test_run_id)
            if run is None:
                raise RuntimeError(f"Unknown test_run_id={test_run_id}!")
            draft: Optional[Draft] = (
                self.session.query(Draft)
                .filter(Draft.test_run_id == run.id, Draft.text == run.scenario.text)
                .one_or_none()
            )

        if draft:
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

    feature_id = sa.Column(sa.Integer(), sa.ForeignKey(Feature.id), nullable=False, index=True)
    test_run_id = sa.Column(sa.Integer(), sa.ForeignKey(TestRun.id), nullable=False)
    text = sa.Column(sa.Text(), doc="Released scenario text")
    pr_url = sa.Column(sa.String(), doc="Absolute pull-request URL", nullable=True)
    published_by = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Draft publisher login", nullable=False)
    published_at = sa.Column(sa.DateTime(timezone=True), doc="Publication time")
    traceback = sa.Column(sa.Text(), doc="Text storage for error traceback", nullable=True)
    status = sa.Column(sa.Enum(DraftStatus), doc="Version publishing status", nullable=False)

    feature = so.relationship(Feature, backref=so.backref("versions", cascade="all, delete-orphan"))

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

    name = sa.Column(sa.String(), nullable=False, unique=True)
    feature_type_id = sa.Column(sa.Integer(), sa.ForeignKey(FeatureType.id), nullable=False, doc="Feature types choice")
    specification = sa.Column(sa.JSON(none_as_null=True))
    created_by = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Author login", nullable=False)

    feature_type = so.relationship(FeatureType)


class Emulation(BaseTable, PrimaryKeyMixin):
    """Emulation templates table."""

    name = sa.Column(sa.String(), nullable=False, unique=True)
    test_user_id = sa.Column(sa.Integer(), sa.ForeignKey(TestUser.id), nullable=False, doc="Test user ID")
    command = sa.Column(sa.String(), nullable=False, doc="Command for emulator's execution")
    created_by = sa.Column(sa.String(), sa.ForeignKey(UserRole.login), doc="Author login", nullable=False)
    test_user = so.relationship(TestUser, backref=so.backref("emulations", cascade="all, delete-orphan"))


class EmulationRun(BaseTable, PrimaryKeyMixin):
    """Emulation runs table."""

    __tablename__ = "emulation_run"  # type: ignore
    emulation_id = sa.Column(sa.Integer(), sa.ForeignKey(Emulation.id), nullable=False, index=True)
    status = sa.Column(sa.Enum(EmulationStatus), doc="Current emulation status", nullable=False)
    changed_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    port = sa.Column(sa.Integer(), doc="Port for emulation")
    traceback = sa.Column(sa.Text(), doc="Text storage for error traceback")
    initiated_by = sa.Column(
        sa.String(), sa.ForeignKey(UserRole.login), doc="Initiator of start emulation", nullable=False
    )

    emulation = so.relationship(Emulation, backref=so.backref("emulation_runs", cascade="all, delete-orphan"))

    def __init__(self, emulation_id: int, initiated_by: str) -> None:
        self.emulation_id = emulation_id
        self.status = EmulationStatus.CREATED
        self.initiated_by = initiated_by
