from datetime import datetime
from typing import Final, Optional

from pydantic import BaseModel, Field


class GitlabRepository(BaseModel):
    """ Model for Gitlab merge-request repository. """

    id: str = Field(..., alias="project_id")


class GitlabBranch(BaseModel):
    """ Model for Gitlab merge-request branch. """

    id: str = Field(..., alias="project_id")
    branch: str = Field(...)
    ref: str = "master"


class GitlabMrRequest(BaseModel):
    """ Model for Gitlab merge-request request. """

    id: str = Field(..., alias="project_id")
    source_branch: GitlabBranch = Field(...)
    target_branch: GitlabBranch = Field(...)
    title: Optional[str]
    description: Optional[str]


class GitlabMrCreationResponse(BaseModel):
    """ Model for Gitlab merge-request creation response. """

    created_at: datetime
    updated_at: datetime
    web_url: Optional[str]
    traceback: Optional[Exception]
    state: str

    class Config:
        arbitrary_types_allowed = True

    def get_mr_url(self) -> str:
        if isinstance(self.web_url, str):
            return self.web_url
        raise RuntimeError("Could not get merge-request URL from response!")


AnyGitlabResponseModel = GitlabMrCreationResponse
GITLAB_RESPONSE_MODELS: Final = [GitlabMrCreationResponse]
