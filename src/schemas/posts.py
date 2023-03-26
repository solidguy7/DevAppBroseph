from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from schemas.comments import CommentResponse

class PostIn(BaseModel):
    name: str
    description: str

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

class PostResponse(PostIn):
    id: UUID
    created: datetime
    updated: Optional[datetime]
    comments: List[CommentResponse]
