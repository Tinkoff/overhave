from datetime import datetime

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
    web_url: str
