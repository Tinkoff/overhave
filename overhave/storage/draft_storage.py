import abc
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

from overhave import db
from overhave.storage import DraftModel
from overhave.utils import get_current_time


class IDraftStorage(abc.ABC):
    """Abstract class for scenario versions storage."""

    @staticmethod
    @abc.abstractmethod
    def draft_model_by_id(session: so.Session, draft_id: int) -> DraftModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_last_published_at_for_feature(feature_id: int) -> datetime | None:
        pass

    @classmethod
    @abc.abstractmethod
    def get_or_create_draft(
        cls, session: so.Session, test_run: db.TestRun, published_by: str, status: db.DraftStatus
    ) -> int:
        pass

    @staticmethod
    @abc.abstractmethod
    def save_response(
        draft_id: int, pr_url: str | None, published_at: datetime, status: db.DraftStatus, traceback: str | None = None
    ) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def save_response_as_duplicate(draft_id: int, feature_id: int, traceback: str | None) -> None:
        pass

    @abc.abstractmethod
    def set_draft_status(self, draft_id: int, status: db.DraftStatus, traceback: str | None = None) -> None:
        pass


class BaseDraftStorageException(Exception):
    """Base exception for :class:`DraftStorage`."""


class NullableScenarioError(BaseDraftStorageException):
    """Exception for situation when Scenario text is None."""


class DraftNotFoundError(BaseDraftStorageException):
    """Exception for situation when draft not found."""


class FeatureNotFoundError(BaseDraftStorageException):
    """Exception for situation when feature not found by feature_id from draft."""


class DraftStorage(IDraftStorage):
    """Class for scenario versions storage."""

    @staticmethod
    def draft_model_by_id(session: so.Session, draft_id: int) -> DraftModel:
        draft = session.query(db.Draft).filter(db.Draft.id == draft_id).one()
        return DraftModel.from_orm(draft)

    @staticmethod
    def get_last_published_at_for_feature(feature_id: int) -> datetime | None:
        with db.create_session() as session:
            last_draft_with_published_at = (
                session.query(db.Draft)
                .filter(db.Draft.feature_id == feature_id, db.Draft.published_at.isnot(None))
                .order_by(db.Draft.id.desc())
                .first()
            )
            if last_draft_with_published_at is None:
                return None
            return last_draft_with_published_at.published_at

    @staticmethod
    def _get_draft_id_by_testrun_id(session: so.Session, test_run_id: int) -> int | None:
        draft = session.query(db.Draft).filter(db.Draft.test_run_id == test_run_id).one_or_none()
        if draft is None:
            return None
        return draft.id

    @staticmethod
    def _create_draft(session: so.Session, test_run: db.TestRun, published_by: str, status: db.DraftStatus) -> int:
        text = test_run.scenario.text
        if text is None:
            raise NullableScenarioError(f"TestRun.id={test_run.id} has Scenario without text!")
        draft = db.Draft(
            feature_id=test_run.scenario.feature_id,
            test_run_id=test_run.id,
            text=text,
            published_by=published_by,
            status=status,
        )
        session.add(draft)
        session.flush()
        return draft.id

    @classmethod
    def get_or_create_draft(
        cls, session: so.Session, test_run: db.TestRun, published_by: str, status: db.DraftStatus
    ) -> int:
        draft_id = cls._get_draft_id_by_testrun_id(session=session, test_run_id=test_run.id)
        if draft_id is not None:
            return draft_id
        return cls._create_draft(session=session, test_run=test_run, published_by=published_by, status=status)

    @staticmethod
    def save_response(
        draft_id: int, pr_url: str | None, published_at: datetime, status: db.DraftStatus, traceback: str | None = None
    ) -> None:
        with db.create_session() as session:
            draft = session.get(db.Draft, draft_id)
            if draft is None:
                raise DraftNotFoundError(f"Draft with id={draft_id} not found!")
            draft.pr_url = pr_url
            draft.published_at = published_at
            if traceback is not None:
                draft.traceback = traceback
            draft.status = status
            feature = session.get(db.Feature, draft.feature_id)
            if feature is None:
                raise FeatureNotFoundError(f"Feature with id={draft.feature_id} not found!")
            feature.released = status.is_succeed

    @staticmethod
    def save_response_as_duplicate(draft_id: int, feature_id: int, traceback: str | None) -> None:
        with db.create_session() as session:
            last_drafts = (
                session.query(db.Draft)
                .filter(db.Draft.feature_id == feature_id)
                .order_by(db.Draft.id.desc())
                .limit(2)
                .all()
            )
            if not last_drafts:
                raise DraftNotFoundError("No one draft exists for Feature.id=%s", feature_id)
            values = dict(status=db.DraftStatus.DUPLICATE, traceback=traceback, published_at=get_current_time())

            # check that previous draft exists and succeed
            if len(last_drafts) > 1 and last_drafts[1].status.is_succeed:
                previous_draft = last_drafts[1]
                values["pr_url"] = previous_draft.pr_url
                values["published_at"] = previous_draft.published_at
            session.execute(sa.Update(db.Draft).where(db.Draft.id == draft_id).values(**values))

    def set_draft_status(self, draft_id: int, status: db.DraftStatus, traceback: str | None = None) -> None:
        with db.create_session() as session:
            query = sa.update(db.Draft).where(db.Draft.id == draft_id).values(status=status)
            if isinstance(traceback, str):
                query = query.values(traceback=traceback)
            session.execute(query)
