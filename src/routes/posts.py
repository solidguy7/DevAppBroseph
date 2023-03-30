from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy import select, insert, update, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from auth.authenticate import authenticate
from database.connection import get_session
from models.users import User, user_post
from models.channels import Channel
from models.posts import Post
from schemas.posts import PostResponse, PostIn

post_router = APIRouter(tags=['Posts'])

@post_router.get('/', response_model=List[PostResponse])
async def get_all_posts(session: AsyncSession = Depends(get_session)) -> List[PostResponse]:
    results = await session.execute(select(Post))
    return list(results.scalars().all())

@post_router.get('/{id}', response_model=PostResponse)
async def get_post(id: UUID, session: AsyncSession = Depends(get_session)) -> PostResponse:
    result = await session.get(entity=Post, ident=id)
    return result

@post_router.post('/{id}')
async def create_post(id: UUID, post: PostIn, user: str = Depends(authenticate), session: AsyncSession = Depends(
    get_session)) -> dict:
    channel_user_id = await session.execute(select(Channel.user_id).where(Channel.id == id))
    user_id = await session.execute(select(User.id).where(User.username == user))
    if channel_user_id.scalar() != user_id.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='You don`t have such a post')
    result = await session.execute(select(Channel).where(Channel.id == id))
    if not result.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no such a channel')
    await session.execute(insert(Post).values(channel_id=id, **post.dict()))
    await session.commit()
    return {'message': 'Post created successfully'}

@post_router.post('/like/{id}')
async def like(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(
    get_session)) -> dict:
    user_id = await session.execute(select(User.id).where(User.username == user))
    user_id = user_id.scalar()
    check = await session.execute(
        select(exists().where(user_post.c.user_id == user_id).where(user_post.c.post_id == id)))
    if check.scalar():
        await session.execute(delete(user_post).where(user_post.c.user_id == user_id).where(user_post.c.post_id == id))
        await session.commit()
        return {'message': 'You unliked this post successfully'}
    await session.execute(insert(user_post).values(user_id=user_id, post_id=id))
    await session.commit()
    return {'message': 'You liked this post successfully'}

@post_router.put('/{id}', response_model=PostResponse)
async def update_post(id: UUID, post: PostIn, user: str = Depends(authenticate),
                         session: AsyncSession = Depends(get_session)) -> PostResponse:
    post_channel_id = await session.execute(select(Post.channel_id).where(Post.id == id))
    user_id = await session.execute(select(User.id).where(User.username == user))
    channel_id = await session.execute(select(Channel.id).where(Channel.user_id == user_id))
    if post_channel_id.scalar() != channel_id.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='You don`t have such a post')
    await session.execute(update(Post).where(Post.id == id).values(**post.dict()))
    await session.commit()
    result = await session.get(entity=Post, ident=id)
    return result

@post_router.delete('/{id}')
async def delete_post(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(
    get_session)) -> dict:
    post_channel_id = await session.execute(select(Post.channel_id).where(Post.id == id))
    user_id = await session.execute(select(User.id).where(User.username == user))
    channel_id = await session.execute(select(Channel.id).where(Channel.user_id == user_id))
    if post_channel_id.scalar() != channel_id.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='You don`t have such a post')
    await session.execute(delete(Post).where(Post.id == id))
    await session.commit()
    return {'message': 'Channel deleted successfully'}
