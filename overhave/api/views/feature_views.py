import logging
from http import HTTPStatus
from typing import List, Optional

import fastapi

from overhave.api.deps import get_feature_storage, get_feature_tag_storage
from overhave.api.views.tags_views import tags_item_handler
from overhave.storage import FeatureModel, IFeatureStorage, IFeatureTagStorage

logger = logging.getLogger(__name__)


def get_features_handler(
    tag_id: Optional[int] = None,
    tag_value: Optional[str] = None,
    feature_storage: IFeatureStorage = fastapi.Depends(get_feature_storage),
    tag_storage: IFeatureTagStorage = fastapi.Depends(get_feature_tag_storage),
) -> List[FeatureModel]:
    if tag_id is not None:
        logger.info("Getting %s by tag_id=%s...", FeatureModel.__name__, tag_id)
        return feature_storage.get_features_by_tag(tag_id=tag_id)
    if tag_value is not None:
        logger.info("Getting %s by tag_value=%s...", FeatureModel.__name__, tag_value)
        tag_model = tags_item_handler(value=tag_value, feature_tag_storage=tag_storage)
        return feature_storage.get_features_by_tag(tag_id=tag_model.id)
    raise fastapi.HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="'tag_id' or 'tag_value' query parameter should be set"
    )
