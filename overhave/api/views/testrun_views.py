from http import HTTPStatus

import fastapi

from overhave.api.deps import get_feature_storage, get_feature_tag_storage, get_redis_producer, get_test_run_storage
from overhave.api.views.tags_views import tags_item_handler
from overhave.storage import IFeatureStorage, IFeatureTagStorage, TestRunModel, TestRunStorage
from overhave.transport import RedisProducer, TestRunData, TestRunTask


def get_test_run_handler(
    test_run_id: int,
    test_run_storage: TestRunStorage = fastapi.Depends(get_test_run_storage),
) -> TestRunModel:
    test_run = test_run_storage.get_test_run(test_run_id)
    if test_run is not None:
        return test_run
    raise fastapi.HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail=f"Test run with id ='{test_run_id}' not found"
    )


def run_tests_by_tag_handler(
    tag_value: str,
    feature_storage: IFeatureStorage = fastapi.Depends(get_feature_storage),
    tag_storage: IFeatureTagStorage = fastapi.Depends(get_feature_tag_storage),
    test_run_storage: TestRunStorage = fastapi.Depends(get_test_run_storage),
    redis_producer: RedisProducer = fastapi.Depends(get_redis_producer),
) -> list[int]:
    tag_model = tags_item_handler(value=tag_value, feature_tag_storage=tag_storage)
    features = feature_storage.get_features_by_tag(tag_id=tag_model.id)
    if not features:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"Features with tag='{tag_value}' do not exist"
        )
    test_run_ids: list[int] = []
    for feature in features:
        test_run_id = test_run_storage.create_test_run(scenario_id=feature.id, executed_by=feature.last_edited_by)
        redis_producer.add_task(TestRunTask(data=TestRunData(test_run_id=test_run_id)))
        test_run_ids.append(test_run_id)
    return test_run_ids
