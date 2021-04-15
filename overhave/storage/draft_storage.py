import abc
from datetime import datetime
from typing import List, Optional, cast

from overhave import db
from overhave.entities import DraftModel


class IDraftStorage(abc.ABC):
    """ Abstract class for scenario versions storage. """

    @abc.abstractmethod
    def get_draft(self, draft_id: int) -> Optional[DraftModel]:
        pass

    @abc.abstractmethod
    def save_draft(self, test_run_id: int, published_by: str) -> int:
        pass

    @abc.abstractmethod
    def save_response(self, draft_id: int, pr_url: str, published_at: datetime, opened: bool) -> None:
        pass

    @abc.abstractmethod
    def get_previous_feature_draft(self, feature_id: int) -> DraftModel:
        pass


class BaseDraftStorageException(Exception):
    """ Base exception for :class:`DraftStorage`. """


class UniqueDraftCreationError(BaseDraftStorageException):
    """ Exception for draft creation error with `as_unique`. """


class NullableDraftsError(BaseDraftStorageException):
    """ Exception for situation with not existing drafts. """


class DraftStorage(IDraftStorage):
    """ Class for scenario versions storage. """

    def get_draft(self, draft_id: int) -> Optional[DraftModel]:
        with db.create_session() as session:
            draft: Optional[db.Draft] = session.query(db.Draft).get(draft_id)
            if draft is not None:
                return cast(DraftModel, DraftModel.from_orm(draft))
            return None

    def save_draft(self, test_run_id: int, published_by: str) -> int:
        with db.create_session() as session:
            try:
                draft = session.query(db.Draft).as_unique(test_run_id=test_run_id, published_by=published_by)
            except RuntimeError as e:
                raise UniqueDraftCreationError("Could not get unique draft!") from e
            session.add(draft)
            session.flush()
            return cast(int, draft.id)

    def save_response(self, draft_id: int, pr_url: str, published_at: datetime, opened: bool) -> None:
        with db.create_session() as session:
            draft: db.Draft = session.query(db.Draft).get(draft_id)
            draft.pr_url = pr_url
            draft.published_at = published_at
            feature: db.Feature = session.query(db.Feature).get(draft.feature_id)
            feature.released = opened

    def get_previous_feature_draft(self, feature_id: int) -> DraftModel:
        with db.create_session() as session:
            selection_num = 2
            drafts: List[db.Draft] = session.query(db.Draft).filter(db.Draft.feature_id == feature_id).order_by(
                db.Draft.id.asc()
            ).limit(selection_num).all()
            if not drafts or len(drafts) != selection_num:
                raise NullableDraftsError(f"Haven't got Drafts amount={selection_num} for feature_id={feature_id}!")
            return cast(DraftModel, DraftModel.from_orm(drafts[0]))
