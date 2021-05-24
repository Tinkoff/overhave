from datetime import datetime
from typing import Dict, Final, List, Optional, Union

from pydantic import BaseModel, Field, validator


class GitlabProject(BaseModel):
    """ Model for Gitlab merge-request project slug. """

    key: str


class GitlabRepository(BaseModel):
    """ Model for Gitlab merge-request repository. """

    name: str = Field(..., alias="slug")
    project: GitlabProject


class GitlabBranch(BaseModel):
    """ Model for Gitlab merge-request branch. """

    branch: str = Field(..., alias="id")
    repository: GitlabRepository

    @validator("branch")
    def insert_refs(cls, v: str) -> str:
        return "refs/heads/" + v


class GitlabReviewerInfo(BaseModel):
    """ Model for Gitlab merge-request reviewer information. """

    name: str


class GitlabReviewer(BaseModel):
    """ Model for Gitlab merge-request reviewer. """

    user: GitlabReviewerInfo


class GitlabBasicMrInfo(BaseModel):
    """ Model for Gitlab basic merge-request information. """

    title: Optional[str]
    open: bool


class GitlabMrRequest(GitlabBasicMrInfo):
    """ Model for Gitlab merge-request request. """

    description: str
    state: str = "OPEN"
    closed: bool = False
    source_branch: GitlabBranch = Field(..., alias="fromRef")
    target_branch: GitlabBranch = Field(..., alias="toRef")
    locked: bool = False
    close_source_branch: bool = True
    reviewers: List[GitlabReviewer]


GitlabLinksType = Dict[str, List[Dict[str, str]]]


class GitlabMrCreationResponse(GitlabBasicMrInfo):
    """ Model for Gitlab merge-request creation response. """

    created_date: datetime = Field(..., alias="createdDate")
    updated_date: datetime = Field(..., alias="updatedDate")
    merge_request_url: Optional[str]
    traceback: Optional[Exception]
    links: Optional[GitlabLinksType]

    class Config:
        arbitrary_types_allowed = True

    def get_mr_url(self) -> str:
        if isinstance(self.merge_request_url, str):
            return self.merge_request_url
        if self.links is not None:
            return self.links["self"][0]["href"]
        raise RuntimeError("Could not get merge-request URL from response!")


class GitlabRequestError(BaseModel):
    """ Model for Gitlab request error. """

    context: Optional[str]
    message: str
    exception_name: str = Field(..., alias="exceptionName")


class GitlabErrorResponse(BaseModel):
    """ Model for Gitlab error response. """

    errors: List[GitlabRequestError]

    @property
    def duplicate(self) -> bool:
        for error in self.errors:
            if not error.exception_name.endswith("DuplicateMergeRequestException"):
                continue
            return True
        return False


AnyGitlabResponseModel = Union[GitlabMrCreationResponse, GitlabErrorResponse]
GITLAB_RESPONSE_MODELS: Final = [GitlabMrCreationResponse, GitlabErrorResponse]
