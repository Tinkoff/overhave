from datetime import datetime
from typing import Dict, Final, List, Optional, Union

from pydantic import BaseModel, Field, validator


class GitlabRepository(BaseModel):
    """ Model for Gitlab merge-request repository. """

    id: str = Field(..., alias="slug")


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
    state: str


class GitlabMrRequest(GitlabBasicMrInfo):
    """ Model for Gitlab merge-request request. """

    description: str
    state: str = "opened"
    closed: bool = False
    source_branch: GitlabBranch = Field(..., alias="fromRef")
    target_branch: GitlabBranch = Field(..., alias="toRef")
    locked: bool = False
    close_source_branch: bool = True
    reviewers: List[GitlabReviewer]


GitlabLinksType = Dict[str, List[Dict[str, str]]]


class GitlabMrCreationResponse(GitlabBasicMrInfo):
    """ Model for Gitlab merge-request creation response. """

    created_at: datetime = Field(..., alias="created_at")
    updated_at: datetime = Field(..., alias="updated_at")
    web_url: Optional[str]
    traceback: Optional[Exception]
    links: Optional[GitlabLinksType]

    class Config:
        arbitrary_types_allowed = True

    def get_mr_url(self) -> str:
        if isinstance(self.web_url, str):
            return self.web_url
        if self.links is not None:
            return self.links["self"][0]["href"]
        raise RuntimeError("Could not get merge-request URL from response!")


class GitlabRequestError(BaseModel):
    """ Model for Gitlab request error. """

    context: Optional[str]
    message: List[str]
    exception_name: str = Field(..., alias="exceptionName")


class GitlabErrorResponse(BaseModel):
    """ Model for Gitlab error response. """

    errors: List[GitlabRequestError]

    @property
    def duplicate(self) -> bool:
        for error in self.errors:
            if len(error.message) == 0 or not error.message[0].startswith(
                "Another open merge request already exists for this source branch"
            ):
                continue
            return True
        return False


AnyGitlabResponseModel = Union[GitlabMrCreationResponse, GitlabErrorResponse]
GITLAB_RESPONSE_MODELS: Final = [GitlabMrCreationResponse, GitlabErrorResponse]
