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

class HTTP_200_SUCCESS(BaseModel):
    message: str = 'Post created successfully'

class DELETE_200_SUCCESS(BaseModel):
    message: str = 'Post deleted successfully'

class LIKE_200_SUCCESS(BaseModel):
    message: str = 'You liked this post successfully or You unliked this post successfully'

class HTTP_404_NOT_FOUND(BaseModel):
    detail: str = 'User doesn`t have such a post'
