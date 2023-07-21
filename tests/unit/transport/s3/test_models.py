from datetime import datetime
from typing import Any

from overhave.transport.s3.models import (
    LIST_BUCKET_MODEL_ADAPTER,
    LIST_OBJECT_MODEL_ADAPTER,
    BucketModel,
    DeletedObjectModel,
    DeletionResultModel,
    NotDeletedObjectModel,
    ObjectModel,
    OwnerModel,
)


class TestBoto3Models:
    """Unit tests for boto3 response models."""

    def test_bucket_model(self, test_bucket_name: str, test_bucket_creation_date: datetime) -> None:
        item = {"Name": test_bucket_name, "CreationDate": test_bucket_creation_date}
        model = BucketModel.model_validate(item)
        assert model.name == test_bucket_name
        assert model.created_at == test_bucket_creation_date
        assert model.model_dump(by_alias=True) == item

    def test_bucket_list(self, test_bucket_name: str, test_bucket_creation_date: datetime) -> None:
        item = {"Name": test_bucket_name, "CreationDate": test_bucket_creation_date}
        model = LIST_BUCKET_MODEL_ADAPTER.validate_python([item])
        assert len(model) == 1
        assert model[0].model_dump(by_alias=True) == item

    def test_object_list(self, test_object_dict: dict[str, Any]) -> None:
        model = LIST_OBJECT_MODEL_ADAPTER.validate_python([test_object_dict])
        assert len(model) == 1
        assert model[0].model_dump(by_alias=True) == test_object_dict

    def test_object_model(self, test_object_dict: dict[str, Any]) -> None:
        model = ObjectModel.model_validate(test_object_dict)
        assert model.name == test_object_dict["Key"]
        assert model.modified_at == test_object_dict["LastModified"]
        assert model.etag == test_object_dict["ETag"]
        assert model.owner == OwnerModel.model_validate(test_object_dict["Owner"])

    def test_owner_model(self, test_object_owner: dict[str, str]) -> None:
        model = OwnerModel.model_validate(test_object_owner)
        assert model.name == test_object_owner["DisplayName"]
        assert model.owner_id == test_object_owner["ID"]

    def test_objects_deletion_list(self, test_deletion_result: dict[str, Any]) -> None:
        model = DeletionResultModel.model_validate(test_deletion_result)
        assert model.deleted
        assert not model.errors
        assert not model.requester

    def test_deleted_objects_model(self) -> None:
        item = {"Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip", "VersionId": '"3b2874d7dceb0f5622fcd5621c8382f2"'}
        model = DeletedObjectModel.model_validate(item)
        assert model.name == item["Key"]
        assert model.etag == item["VersionId"]
        assert not model.marker
        assert not model.marker_id

    def test_not_deleted_objects_model(self) -> None:
        item = {
            "Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip",
            "VersionId": '"3b2874d7dceb0f5622fcd5621c8382f2"',
            "Code": "401",
            "Message": "Not allowed",
        }
        model = NotDeletedObjectModel.model_validate(item)
        assert model.name == item["Key"]
        assert model.etag == item["VersionId"]
        assert model.code == item["Code"]
        assert model.message == item["Message"]
