from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PostUpdate(BaseModel):
    name: str
    description: str

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

class PostIn(PostUpdate):
    channel_id: UUID

class PostResponse(PostIn):
    id: UUID
    created: datetime
    updated: Optional[datetime]
