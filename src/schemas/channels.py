from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from models.posts import Post

class ChannelIn(BaseModel):
    name: str
    avatar: Optional[str]
    description: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

class ChannelResponse(ChannelIn):
    id: UUID
    created: datetime
    updated: Optional[datetime]
    user_id: UUID
    # posts: Optional[List[Post]]
