import logging
from contextlib import contextmanager
from typing import Any, Iterator

import sqlalchemy.orm as so
from sqlalchemy.exc import ProgrammingError

from overhave.db.base import Session, metadata
from overhave.db.tables import FeatureType

logger = logging.getLogger(__name__)


@contextmanager
def create_session(**kwargs: Any) -> Iterator[so.Session]:
    """Provide a transactional scope around a series of operations."""
    new_session = Session(bind=metadata.engine, **kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def ensure_feature_types_exist(feature_types: list[str]) -> None:
    with create_session() as session:
        try:
            for feature_type in feature_types:
                existing_type = session.query(FeatureType).filter_by(name=feature_type).one_or_none()
                if existing_type is not None:
                    continue
                session.add(FeatureType(name=feature_type))
                logger.info("Created feature type '%s'", feature_type)
        except ProgrammingError:
            logger.exception("Could not create feature types dynamically!")
