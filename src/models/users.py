from sqlalchemy import Column, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.connection import Base

user_channel = Table('user_channel', Base.metadata,
                    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
                    Column('channel_id', UUID(as_uuid=True), ForeignKey('channels.id')))

user_post = Table('user_post', Base.metadata,
                  Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
                  Column('post_id', UUID(as_uuid=True), ForeignKey('posts.id')))

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    email = Column(String(32), nullable=False, unique=True)
    created = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    following = relationship('Channel', secondary=user_channel, backref='followed', cascade='all, delete')
    likes = relationship('Post', secondary=user_post, backref='liked', cascade='all, delete')
    channels = relationship('Channel', backref='user', cascade='all, delete-orphan')
    comments = relationship('Comment', backref='user', cascade='all, delete-orphan')
