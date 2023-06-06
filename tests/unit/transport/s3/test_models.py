from datetime import datetime
from typing import Any

from pydantic.tools import parse_obj_as

from overhave.transport.s3.models import (
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
        model = BucketModel.parse_obj(item)
        assert model.name == test_bucket_name
        assert model.created_at == test_bucket_creation_date
        assert model.dict(by_alias=True) == item

    def test_bucket_list(self, test_bucket_name: str, test_bucket_creation_date: datetime) -> None:
        item = {"Name": test_bucket_name, "CreationDate": test_bucket_creation_date}
        model = parse_obj_as(list[BucketModel], [item])
        assert len(model) == 1
        assert model[0].dict(by_alias=True) == item

    def test_object_list(self, test_object_dict: dict[str, Any]) -> None:
        model = parse_obj_as(list[ObjectModel], [test_object_dict])
        assert len(model) == 1
        assert model[0].dict(by_alias=True) == test_object_dict

    def test_object_model(self, test_object_dict: dict[str, Any]) -> None:
        model = ObjectModel.parse_obj(test_object_dict)
        assert model.name == test_object_dict["Key"]
        assert model.modified_at == test_object_dict["LastModified"]
        assert model.etag == test_object_dict["ETag"]
        assert model.owner == OwnerModel.parse_obj(test_object_dict["Owner"])

    def test_owner_model(self, test_object_owner: dict[str, str]) -> None:
        model = OwnerModel.parse_obj(test_object_owner)
        assert model.name == test_object_owner["DisplayName"]
        assert model.owner_id == test_object_owner["ID"]

    def test_objects_deletion_list(self, test_deletion_result: dict[str, Any]) -> None:
        model = DeletionResultModel.parse_obj(test_deletion_result)
        assert model.deleted
        assert not model.errors
        assert not model.requester

    def test_deleted_objects_model(self) -> None:
        item = {"Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip", "VersionId": '"3b2874d7dceb0f5622fcd5621c8382f2"'}
        model = DeletedObjectModel.parse_obj(item)
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
        model = NotDeletedObjectModel.parse_obj(item)
        assert model.name == item["Key"]
        assert model.etag == item["VersionId"]
        assert model.code == item["Code"]
        assert model.message == item["Message"]
