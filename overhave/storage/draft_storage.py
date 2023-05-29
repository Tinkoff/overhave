import abc
from datetime import datetime
from typing import cast

from pydantic import parse_obj_as

from overhave import db
from overhave.storage import DraftModel


class IDraftStorage(abc.ABC):
    """Abstract class for scenario versions storage."""

    @staticmethod
    @abc.abstractmethod
    def get_draft(draft_id: int) -> DraftModel | None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_drafts_by_feature_id(feature_id: int) -> list[DraftModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def save_draft(test_run_id: int, published_by: str, status: db.DraftStatus) -> int:
        pass

    @staticmethod
    @abc.abstractmethod
    def save_response(
        draft_id: int, pr_url: str | None, published_at: datetime, status: db.DraftStatus, traceback: str | None = None
    ) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_previous_feature_draft(feature_id: int) -> DraftModel:
        pass

    @abc.abstractmethod
    def set_draft_status(self, draft_id: int, status: db.DraftStatus, traceback: str | None = None) -> None:
        pass


class BaseDraftStorageException(Exception):
    """Base exception for :class:`DraftStorage`."""


class UniqueDraftCreationError(BaseDraftStorageException):
    """Exception for draft creation error with `as_unique`."""


class DraftNotFoundError(BaseDraftStorageException):
    """Exception for situation when draft not found."""


class FeatureNotFoundError(BaseDraftStorageException):
    """Exception for situation when feature not found by feature_id from draft."""


class NullableDraftsError(BaseDraftStorageException):
    """Exception for situation with not existing drafts."""


class DraftStorage(IDraftStorage):
    """Class for scenario versions storage."""

    @staticmethod
    def get_draft(draft_id: int) -> DraftModel | None:
        with db.create_session() as session:
            draft = session.get(db.Draft, draft_id)
            if draft is not None:
                return DraftModel.from_orm(draft)
            return None

    @staticmethod
    def get_drafts_by_feature_id(feature_id: int) -> list[DraftModel]:
        with db.create_session() as session:
            drafts = session.query(db.Draft).filter(db.Draft.feature_id == feature_id).all()
            return parse_obj_as(list[DraftModel], drafts)

    @staticmethod
    def save_draft(test_run_id: int, published_by: str, status: db.DraftStatus) -> int:
        with db.create_session() as session:
            try:
                draft = cast(db.DraftQuery, session.query(db.Draft)).as_unique(
                    test_run_id=test_run_id, published_by=published_by, status=status
                )
            except RuntimeError as e:
                raise UniqueDraftCreationError("Could not get unique draft!") from e
            session.add(draft)
            session.flush()
            return cast(int, draft.id)

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
            feature.released = status.success

    @staticmethod
    def get_previous_feature_draft(feature_id: int) -> DraftModel:
        with db.create_session() as session:
            selection_num = 2
            drafts = (  # noqa: ECE001
                session.query(db.Draft)
                .filter(db.Draft.feature_id == feature_id)
                .order_by(db.Draft.id.desc())
                .limit(selection_num)
                .all()
            )
            if not drafts or len(drafts) != selection_num:
                raise NullableDraftsError(f"Haven't got Drafts amount={selection_num} for feature_id={feature_id}!")
            return DraftModel.from_orm(drafts[0])

    def set_draft_status(self, draft_id: int, status: db.DraftStatus, traceback: str | None = None) -> None:
        with db.create_session() as session:
            draft = session.get(db.Draft, draft_id)
            if draft is None:
                raise DraftNotFoundError(f"Draft with id={draft_id} not found!")
            draft.status = status
            if isinstance(traceback, str):
                draft.traceback = traceback
