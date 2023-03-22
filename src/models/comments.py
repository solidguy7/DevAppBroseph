from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.connection import Base

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(64), nullable=False)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'))
