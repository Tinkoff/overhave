from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Extra, Field, root_validator
from pydantic.main import BaseModel


class BucketModel(BaseModel):
    """Model for boto3 client Bucket."""

    name: str = Field(alias="Name")
    created_at: datetime = Field(alias="CreationDate")


class OwnerModel(BaseModel):
    """Model for boto3 client object owner."""

    name: str = Field(alias="DisplayName")
    owner_id: str = Field(alias="ID")


class ObjectModel(BaseModel):
    """Model for boto3 client object."""

    name: str = Field(alias="Key")
    modified_at: datetime = Field(alias="LastModified")
    etag: str = Field(alias="ETag")
    size: int = Field(alias="Size")
    storage_class: str = Field(alias="StorageClass")
    owner: OwnerModel = Field(alias="Owner")

    class Config:
        extra = Extra.allow


class BaseObjectToDeletionModel(BaseModel):
    """Base model for boto3 client object deletion result."""

    name: str = Field(alias="Key")
    etag: Optional[str] = Field(alias="VersionId")


class DeletedObjectModel(BaseObjectToDeletionModel):
    """Model for boto3 client deleted object."""

    marker: Optional[bool] = Field(alias="DeleteMarker")
    marker_id: Optional[bool] = Field(alias="DeleteMarkerVersionId")


class NotDeletedObjectModel(BaseObjectToDeletionModel):
    """Model for boto3 client not deleted object."""

    code: str = Field(alias="Code")
    message: str = Field(alias="Message")


class DeletionResultModel(BaseModel):
    """Model for boto3 client objects deletion result."""

    deleted: Optional[List[DeletedObjectModel]] = Field(alias="Deleted")
    errors: Optional[List[NotDeletedObjectModel]] = Field(alias="Errors")
    requester: Optional[str] = Field(alias="RequestCharged")

    @root_validator(pre=True)
    def validate_results(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        deleted = values.get("Deleted")
        errors = values.get("Errors")
        if deleted is None and errors is None:
            raise ValueError("At least one result field should be presented!")
        return values
