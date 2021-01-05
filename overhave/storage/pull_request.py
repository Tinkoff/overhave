from overhave import db
from overhave.stash.models import StashPrCreationResponse


def add_pr_url(draft_id: int, response: StashPrCreationResponse) -> None:
    with db.create_session() as session:
        draft: db.Draft = session.query(db.Draft).filter(db.Draft.id == draft_id).one()
        draft.pr_url = response.get_pr_url()
        draft.created_at = response.created_date
        feature: db.Feature = session.query(db.Feature).filter(db.Feature.id == draft.feature.id).one()
        feature.released = response.open


def get_last_pr_url(feature_id: int) -> str:
    with db.create_session() as session:
        draft: db.Draft = session.query(db.Draft).filter(db.Draft.feature_id == feature_id).order_by(
            db.Draft.id.desc()
        ).first()
        return str(draft.pr_url)
