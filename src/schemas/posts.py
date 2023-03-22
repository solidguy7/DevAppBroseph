from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PostIn(BaseModel):
    name: str
    description: str

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

class PostResponse(PostIn):
    id: Optional[UUID]
    created: Optional[datetime]
    updated: Optional[datetime]
    channel_id: Optional[UUID]
