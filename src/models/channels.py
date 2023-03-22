from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.connection import Base

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(32), nullable=False)
    avatar = Column(String(64), nullable=True)
    description = Column(String(64), nullable=True)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    posts = relationship('Post', backref='channel', cascade="all, delete-orphan")
