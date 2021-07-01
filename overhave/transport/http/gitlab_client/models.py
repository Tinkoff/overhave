from typing import List, Optional

from pydantic import BaseModel, Field


class GitlabRepository(BaseModel):
    """ Model for Gitlab merge-request repository. """

    id: str = Field(..., alias="project_id")


class GitlabMrRequest(BaseModel):
    """ Model for Gitlab merge-request request. """

    id: str = Field(..., alias="project_id")
    source_branch: str
    target_branch: str
    title: Optional[str]
    description: Optional[str]
    reviewer_ids: List[str]
