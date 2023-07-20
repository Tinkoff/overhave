from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, TypeAdapter, model_validator


class BucketModel(BaseModel):
    """Model for boto3 client Bucket."""

    name: str = Field(alias="Name")
    created_at: datetime = Field(alias="CreationDate")


LIST_BUCKET_MODEL_ADAPTER: TypeAdapter[list[BucketModel]] = TypeAdapter(list[BucketModel])


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
        extra = "allow"


LIST_OBJECT_MODEL_ADAPTER: TypeAdapter[list[ObjectModel]] = TypeAdapter(list[ObjectModel])


class BaseObjectToDeletionModel(BaseModel):
    """Base model for boto3 client object deletion result."""

    name: str = Field(alias="Key")
    etag: str | None = Field(default=None, alias="VersionId")


class DeletedObjectModel(BaseObjectToDeletionModel):
    """Model for boto3 client deleted object."""

    marker: bool | None = Field(default=None, alias="DeleteMarker")
    marker_id: bool | None = Field(default=None, alias="DeleteMarkerVersionId")


class NotDeletedObjectModel(BaseObjectToDeletionModel):
    """Model for boto3 client not deleted object."""

    code: str = Field(alias="Code")
    message: str = Field(alias="Message")


class DeletionResultModel(BaseModel):
    """Model for boto3 client objects deletion result."""

    deleted: list[DeletedObjectModel] | None = Field(default=None, alias="Deleted")
    errors: list[NotDeletedObjectModel] | None = Field(default=None, alias="Errors")
    requester: str | None = Field(default=None, alias="RequestCharged")

    @model_validator(mode="before")
    def validate_results(cls, values: dict[str, Any]) -> dict[str, Any]:
        deleted = values.get("Deleted")
        errors = values.get("Errors")
        if deleted is None and errors is None:
            raise ValueError("At least one result field should be presented!")
        return values
