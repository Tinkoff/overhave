import logging
from http import HTTPStatus
from typing import List, Optional

import fastapi
import flask
from flask_login import current_user
from yarl import URL

from overhave.api.deps import get_feature_storage, get_feature_tag_storage
from overhave.api.views.tags_views import tags_item_handler, tags_list_handler
from overhave.factory.components.admin_factory import IAdminFactory
from overhave.factory.getters import get_admin_factory
from overhave.storage import FeatureModel, IFeatureStorage, IFeatureTagStorage
from overhave.transport import TestRunData, TestRunTask

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


def run_test_for_procedure_handler(
    procedure_name: str,
    factory: IAdminFactory = fastapi.Depends(get_admin_factory),
) -> List[URL]:
    features = tags_list_handler(procedure_name)
    urls: List[URL] = []
    for feature in features:
        test_run_id = factory.test_run_storage.create_test_run(scenario_id=feature.id, executed_by=current_user.login)
        factory.redis_producer.add_task(TestRunTask(data=TestRunData(test_run_id=test_run_id)))
        urls.append(URL(flask.url_for("testrun.details_view", id=test_run_id)))
    return urls
