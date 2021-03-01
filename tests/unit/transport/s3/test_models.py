from datetime import datetime

from overhave.transport.s3.models import BucketModel, BucketsListModel


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
