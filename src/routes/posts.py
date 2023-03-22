from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from auth import authenticate
from database.connection import get_session
from models.users import User
from models.posts import Post
from schemas.posts import PostResponse, PostIn

post_router = APIRouter(tags=['Posts'])
#
# @post_router.get('/', response_model=PostResponse)
# async def get_all_posts(session: AsyncSession = Depends(get_session)) -> List[PostResponse]:
#     results = await session.execute(select(Post))
#     return list(results.scalars().all())
#
# @post_router.get('/{id}', response_model=PostResponse)
# async def get_channel(id: UUID, session: AsyncSession = Depends(get_session)) -> PostResponse:
#     result = await session.get(entity=Post, ident=id)
#     return result
#
# @post_router.post('/')
# async def create_channel(post: PostIn, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
#     new_post = Post(name=post.name, description=post.description)
#     result = await session.execute(select(User.id).where(User.username == user))
#     new_post.user_id = result.scalar()
#     session.add(new_post)
#     await session.commit()
#     return {'message': 'Channel created successfully'}

# @channel_router.put('/{id}', response_model=ChannelResponse)
# async def update_channel(id: UUID, channel: ChannelUpdate, user: str = Depends(authenticate),
#                          session: AsyncSession = Depends(get_session)) -> ChannelResponse:
#     result = await session.get(entity=Channel, ident=id)
#     if channel.name is not None:
#         result.name = channel.name
#     if channel.avatar is not None:
#         result.avatar = channel.avatar
#     if channel.description is not None:
#         result.description = channel.description
#     session.add(result)
#     await session.commit()
#     return result
#
# @post_router.delete('/{id}')
# async def delete_channel(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
#     result = await session.get(entity=Post, ident=id)
#     await session.delete(result)
#     await session.commit()
#     return {'message': 'Channel deleted successfully'}
