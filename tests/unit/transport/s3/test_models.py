from datetime import datetime

from overhave.transport.s3.models import (
    BucketModel,
    BucketsListModel,
    DeletedObjectModel,
    DeletionResultModel,
    NotDeletedObjectModel,
    ObjectModel,
    ObjectsList,
    OwnerModel,
)


class TestBoto3Models:
    """ Unit tests for boto3 response models. """

    def test_bucket_model(self, test_bucket_name: str, test_bucket_creation_date: datetime):
        item = {"Name": test_bucket_name, "CreationDate": test_bucket_creation_date}
        model = BucketModel.parse_obj(item)
        assert model.name == test_bucket_name
        assert model.created_at == test_bucket_creation_date
        assert model.dict(by_alias=True) == item

    def test_bucket_list(self, test_bucket_name: str, test_bucket_creation_date: datetime):
        item = {"Name": test_bucket_name, "CreationDate": test_bucket_creation_date}
        model = BucketsListModel.parse_obj([item])
        assert len(model.items) == 1
        assert model.items[0].dict(by_alias=True) == item

    def test_object_list(self):
        model = ObjectsList.parse_obj(
            [
                {
                    "Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip",
                    "LastModified": datetime(2021, 2, 28, 18, 37, 40, 219000),
                    "ETag": '"3b2874d7dceb0f5622fcd5621c8382f2"',
                    "Size": 971457,
                    "StorageClass": "STANDARD",
                    "Owner": {"DisplayName": "hello-friend", "ID": "hello-friend"},
                },
                {
                    "Key": "d770f754-79f0-11eb-bbe4-acde48001122.zip",
                    "LastModified": datetime(2021, 2, 28, 18, 12, 35, 735000),
                    "ETag": '"9d5d01b6328a08d156c18e1b0287d846"',
                    "Size": 971447,
                    "StorageClass": "STANDARD",
                    "Owner": {"DisplayName": "hello-friend", "ID": "hello-friend"},
                },
            ]
        )
        assert len(model) == 2

    def test_object_model(self):
        item = {
            "Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip",
            "LastModified": datetime(2021, 2, 28, 18, 37, 40, 219000),
            "ETag": '"3b2874d7dceb0f5622fcd5621c8382f2"',
            "Size": 971457,
            "StorageClass": "STANDARD",
            "Owner": {"DisplayName": "hello-friend", "ID": "hello-friend"},
        }
        model = ObjectModel.parse_obj(item)
        assert model.name == item["Key"]
        assert model.modified_at == item["LastModified"]
        assert model.etag == item["ETag"]
        assert model.owner == OwnerModel.parse_obj(item["Owner"])

    def test_owner_model(self):
        item = {"DisplayName": "hello-friend", "ID": "hello-friend"}
        model = OwnerModel.parse_obj(item)
        assert model.name == item["DisplayName"]
        assert model.owner_id == item["ID"]

    def test_objects_deletion_list(self):
        item = {
            "ResponseMetadata": {
                "RequestId": "tx000000000000002f6d78a-00603f2f05-3380ab-m1-tst",
                "HostId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "transfer-encoding": "chunked",
                    "x-amz-request-id": "tx000000000000002f6d78a-00603f2f05-3380ab-m1-tst",
                    "content-type": "application/xml",
                    "date": "Wed, 03 Mar 2021 06:39:01 GMT",
                },
                "RetryAttempts": 0,
            },
            "Deleted": [
                {"Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip", "VersionId": '"3b2874d7dceb0f5622fcd5621c8382f2"'},
                {"Key": "d770f754-79f0-11eb-bbe4-acde48001122.zip", "VersionId": '"9d5d01b6328a08d156c18e1b0287d846"'},
            ],
        }
        model = DeletionResultModel.parse_obj(item)
        assert model.deleted
        assert not model.errors
        assert not model.requester

    def test_deleted_objects_model(self):
        item = {"Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip", "VersionId": '"3b2874d7dceb0f5622fcd5621c8382f2"'}
        model = DeletedObjectModel.parse_obj(item)
        assert model.name == item["Key"]
        assert model.etag == item["VersionId"]
        assert not model.marker
        assert not model.marker_id

    def test_not_deleted_objects_model(self):
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
