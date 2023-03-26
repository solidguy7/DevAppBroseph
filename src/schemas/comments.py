from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class CommentIn(BaseModel):
    description: str

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

class CommentResponse(CommentIn):
    id: UUID
    created: datetime
    updated: Optional[datetime]
    user_id: UUID
    post_id: UUID
