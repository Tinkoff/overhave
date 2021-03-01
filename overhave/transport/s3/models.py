from datetime import datetime
from typing import List

from pydantic import Field
from pydantic.main import BaseModel


class BucketModel(BaseModel):
    """ Model for boto3 client Bucket. """

    name: str = Field(alias="Name")
    created_at: datetime = Field(alias="CreationDate")


class BucketsListModel(BaseModel):
    """ Model for list of BucketModels. """

    __root__: List[BucketModel]

    @property
    def items(self) -> List[BucketModel]:
        return self.__root__
