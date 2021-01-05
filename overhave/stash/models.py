from datetime import datetime
from typing import Dict, Final, List, Optional, Union

from pydantic import BaseModel, Field, validator


class StashProject(BaseModel):
    key: str


class StashRepository(BaseModel):
    name: str = Field(..., alias='slug')
    project: StashProject


class StashBranch(BaseModel):
    branch: str = Field(..., alias='id')
    repository: StashRepository

    @validator('branch')
    def insert_refs(cls, v: str) -> str:
        return 'refs/heads/' + v


class StashReviewerInfo(BaseModel):
    name: str


class StashReviewer(BaseModel):
    user: StashReviewerInfo


class StashBasicPrInfo(BaseModel):
    title: Optional[str]
    open: bool


class StashPrRequest(StashBasicPrInfo):
    description: str
    state: str = "OPEN"
    closed: bool = False
    source_branch: StashBranch = Field(..., alias='fromRef')
    target_branch: StashBranch = Field(..., alias='toRef')
    locked: bool = False
    close_source_branch: bool = True
    reviewers: List[StashReviewer]


StashLinksType = Dict[str, List[Dict[str, str]]]


class StashPrCreationResponse(StashBasicPrInfo):
    created_date: datetime = Field(..., alias='createdDate')
    updated_date: datetime = Field(..., alias='updatedDate')
    pull_request_url: Optional[str]
    traceback: Optional[Exception]
    links: Optional[StashLinksType]

    class Config:
        arbitrary_types_allowed = True

    def get_pr_url(self) -> str:
        if self.pull_request_url is not None:
            return self.pull_request_url
        if self.links is not None:
            return self.links['self'][0]['href']
        raise RuntimeError("Could not get pull-request URL from response!")


class StashRequestError(BaseModel):
    context: Optional[str]
    message: str
    exception_name: str = Field(..., alias="exceptionName")


class StashErrorResponse(BaseModel):
    errors: List[StashRequestError]

    @property
    def duplicate(self) -> bool:
        for error in self.errors:
            if not error.exception_name.endswith("DuplicatePullRequestException"):
                continue
            return True
        return False


AnyStashResponseModel = Union[StashPrCreationResponse, StashErrorResponse]
STASH_RESPONSE_MODELS: Final = [StashPrCreationResponse, StashErrorResponse]
