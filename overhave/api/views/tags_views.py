import logging
from http import HTTPStatus
from typing import List

import fastapi

from overhave.api.deps import get_feature_tag_storage
from overhave.storage import IFeatureTagStorage, TagModel

logger = logging.getLogger(__name__)


def tags_item_handler(
    value: str,
    feature_tag_storage: IFeatureTagStorage = fastapi.Depends(get_feature_tag_storage),
) -> TagModel:
    logger.info("Getting %s with value='%s...'", TagModel.__name__, value)
    tag_model = feature_tag_storage.get_tag_by_value(value)
    if tag_model is None:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"Tag with value='{value}' does not exist"
        )
    return tag_model


def tags_list_handler(
    value: str,
    feature_tag_storage: IFeatureTagStorage = fastapi.Depends(get_feature_tag_storage),
) -> List[TagModel]:
    logger.info("Getting %s list like value='%s...'", TagModel.__name__, value)
    return feature_tag_storage.get_tags_like_value(value)
