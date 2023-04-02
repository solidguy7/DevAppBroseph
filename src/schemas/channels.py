from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from schemas.posts import PostResponse

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
    posts: List[PostResponse]

class HTTP_200_SUCCESS(BaseModel):
    message: str = 'Channel created successfully'

class DELETE_200_SUCCESS(BaseModel):
    message: str = 'Channel deleted successfully'

class FOLLOW_200_SUCCESS(BaseModel):
    message: str = 'You followed this channel successfully or You unfollowed this channel successfully'

class HTTP_404_NOT_FOUND(BaseModel):
    detail: str = 'User doesn`t have such a channel'

class HTTP_406_NOT_ACCEPTABLE(BaseModel):
    detail: str = 'You can`t follow your channels'
