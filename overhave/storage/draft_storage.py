import abc
from datetime import datetime
from typing import List, Optional, cast

from overhave import db
from overhave.db import DraftStatus
from overhave.entities import DraftModel


class IDraftStorage(abc.ABC):
    """Abstract class for scenario versions storage."""

    @staticmethod
    @abc.abstractmethod
    def get_draft(draft_id: int) -> Optional[DraftModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_drafts_by_feature_id(feature_id: int) -> List[DraftModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def save_draft(test_run_id: int, published_by: str, status: DraftStatus) -> int:
        pass

    @staticmethod
    @abc.abstractmethod
    def save_response(
        draft_id: int, pr_url: str, published_at: datetime, status: DraftStatus, traceback: Optional[str] = None
    ) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_previous_feature_draft(feature_id: int) -> DraftModel:
        pass

    @abc.abstractmethod
    def set_draft_status(self, draft_id: int, status: DraftStatus, traceback: Optional[str] = None) -> None:
        pass


class BaseDraftStorageException(Exception):
    """Base exception for :class:`DraftStorage`."""


class UniqueDraftCreationError(BaseDraftStorageException):
    """Exception for draft creation error with `as_unique`."""


class NullableDraftsError(BaseDraftStorageException):
    """Exception for situation with not existing drafts."""


class DraftStorage(IDraftStorage):
    """Class for scenario versions storage."""

    @staticmethod
    def get_draft(draft_id: int) -> Optional[DraftModel]:
        with db.create_session() as session:
            draft: Optional[db.Draft] = session.query(db.Draft).get(draft_id)
            if draft is not None:
                return cast(DraftModel, DraftModel.from_orm(draft))
            return None

    @staticmethod
    def get_drafts_by_feature_id(feature_id: int) -> List[DraftModel]:
        draft_model_list: List[DraftModel] = []
        with db.create_session() as session:
            drafts: List[db.Draft] = session.query(db.Draft).filter(db.Draft.feature_id == feature_id).all()
            for draft in drafts:
                draft_model_list.append(cast(DraftModel, DraftModel.from_orm(draft)))
        return draft_model_list

    @staticmethod
    def save_draft(test_run_id: int, published_by: str, status: DraftStatus) -> int:
        with db.create_session() as session:
            try:
                draft = session.query(db.Draft).as_unique(
                    test_run_id=test_run_id, published_by=published_by, status=status
                )
            except RuntimeError as e:
                raise UniqueDraftCreationError("Could not get unique draft!") from e
            session.add(draft)
            session.flush()
            return cast(int, draft.id)

    @staticmethod
    def save_response(
        draft_id: int, pr_url: str, published_at: datetime, status: DraftStatus, traceback: Optional[str] = None
    ) -> None:
        with db.create_session() as session:
            draft: db.Draft = session.query(db.Draft).get(draft_id)
            draft.pr_url = pr_url
            draft.published_at = published_at
            if traceback is not None:
                draft.traceback = traceback
            draft.status = status
            feature: db.Feature = session.query(db.Feature).get(draft.feature_id)
            feature.released = status.success

    @staticmethod
    def get_previous_feature_draft(feature_id: int) -> DraftModel:
        with db.create_session() as session:
            selection_num = 2
            drafts: List[db.Draft] = (  # noqa: ECE001
                session.query(db.Draft)
                .filter(db.Draft.feature_id == feature_id)
                .order_by(db.Draft.id.asc())
                .limit(selection_num)
                .all()
            )
            if not drafts or len(drafts) != selection_num:
                raise NullableDraftsError(f"Haven't got Drafts amount={selection_num} for feature_id={feature_id}!")
            return cast(DraftModel, DraftModel.from_orm(drafts[0]))

    def set_draft_status(self, draft_id: int, status: DraftStatus, traceback: Optional[str] = None) -> None:
        with db.create_session() as session:
            draft: db.Draft = session.query(db.Draft).get(draft_id)
            draft.status = status
            if not isinstance(traceback, str):
                return
            draft.traceback = traceback
