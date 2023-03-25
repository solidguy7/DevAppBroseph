from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.connection import Base

class Post(Base):
    __tablename__ = 'posts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(32), nullable=False)
    description = Column(String(64), nullable=False)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())
    channel_id = Column(UUID(as_uuid=True), ForeignKey('channels.id'))
    comments = relationship('Comment', backref='post', cascade="all, delete-orphan", lazy='selectin')
