from datetime import datetime
from typing import Final

from pydantic import BaseModel, Field


class GitlabRepository(BaseModel):
    """Model for Gitlab merge-request repository."""

    id: str = Field(..., alias="project_id")


class GitlabMrRequest(BaseModel):
    """Model for Gitlab merge-request request."""

    id: str = Field(..., alias="project_id")
    source_branch: str
    target_branch: str
    title: str | None
    description: str | None
    reviewer_ids: list[str]


class GitlabMrCreationResponse(BaseModel):
    """Model for Gitlab merge-request creation response."""

    created_at: datetime
    updated_at: datetime
    web_url: str | None
    traceback: Exception | None
    state: str

    class Config:
        arbitrary_types_allowed = True

    @property
    def get_mr_url(self) -> str:
        if isinstance(self.web_url, str):
            return self.web_url
        raise RuntimeError("Could not get merge-request URL from response!")


AnyGitlabResponseModel = GitlabMrCreationResponse
GITLAB_RESPONSE_MODELS: Final = [GitlabMrCreationResponse]
