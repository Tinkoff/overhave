import logging
from http import HTTPStatus
from typing import List, Optional

import fastapi

from overhave.api.deps import get_draft_storage, get_feature_storage, get_feature_tag_storage
from overhave.api.views.tags_views import tags_item_handler
from overhave.storage import FeatureModel, IDraftStorage, IFeatureStorage, IFeatureTagStorage

logger = logging.getLogger(__name__)


def _get_features_by_tag_id_handler(tag_id: int, feature_storage: IFeatureStorage) -> List[FeatureModel]:
    logger.info("Getting %s by tag_id=%s...", FeatureModel.__name__, tag_id)
    return feature_storage.get_features_by_tag(tag_id=tag_id)


def get_features_handler(
    tag_id: Optional[int] = None,
    tag_value: Optional[str] = None,
    has_releases: bool = True,
    feature_storage: IFeatureStorage = fastapi.Depends(get_feature_storage),
    tag_storage: IFeatureTagStorage = fastapi.Depends(get_feature_tag_storage),
    draft_storage: IDraftStorage = fastapi.Depends(get_draft_storage),
) -> List[FeatureModel]:
    if tag_id is not None:
        return _get_features_by_tag_id_handler(tag_id=tag_id, feature_storage=feature_storage)
    if tag_value is not None:
        tag_model = tags_item_handler(value=tag_value, feature_tag_storage=tag_storage)
        return _get_features_by_tag_id_handler(tag_id=tag_model.id, feature_storage=feature_storage)
    raise fastapi.HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="'tag_id' or 'tag_value' query parameter should be set"
    )
