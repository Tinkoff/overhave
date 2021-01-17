from datetime import datetime
from typing import Dict, Final, List, Optional, Union

from pydantic import BaseModel, Field, validator


class StashProject(BaseModel):
    """ Model for Stash pull-request project slug. """

    key: str


class StashRepository(BaseModel):
    """ Model for Stash pull-request repository. """

    name: str = Field(..., alias='slug')
    project: StashProject


class StashBranch(BaseModel):
    """ Model for Stash pull-request branch. """

    branch: str = Field(..., alias='id')
    repository: StashRepository

    @validator('branch')
    def insert_refs(cls, v: str) -> str:
        return 'refs/heads/' + v


class StashReviewerInfo(BaseModel):
    """ Model for Stash pull-request reviewer information. """

    name: str


class StashReviewer(BaseModel):
    """ Model for Stash pull-request reviewer. """

    user: StashReviewerInfo


class StashBasicPrInfo(BaseModel):
    """ Model for Stash basic pull-request information. """

    title: Optional[str]
    open: bool


class StashPrRequest(StashBasicPrInfo):
    """ Model for Stash pull-request request. """

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
    """ Model for Stash pull-request creation response. """

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
    """ Model for Stash request error. """

    context: Optional[str]
    message: str
    exception_name: str = Field(..., alias="exceptionName")


class StashErrorResponse(BaseModel):
    """ Model for Stash error response. """

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
