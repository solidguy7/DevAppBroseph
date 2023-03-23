from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from auth.authenticate import authenticate
from database.connection import get_session
from models.users import User
from models.channels import Channel
from models.posts import Post
from schemas.posts import PostResponse, PostIn

post_router = APIRouter(tags=['Posts'])

@post_router.get('/', response_model=PostResponse)
async def get_all_posts(session: AsyncSession = Depends(get_session)) -> List[PostResponse]:
    results = await session.execute(select(Post))
    return list(results.scalars().all())

@post_router.get('/{id}', response_model=PostResponse)
async def get_post(id: UUID, session: AsyncSession = Depends(get_session)) -> PostResponse:
    result = await session.get(entity=Post, ident=id)
    return result

@post_router.post('/')
async def create_post(post: PostIn, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(Channel.id).where(User.username == user))
    await session.execute(insert(Post).values(channel_id=result.scalar(), **post.dict()))
    await session.commit()
    return {'message': 'Post created successfully'}

@post_router.put('/{id}', response_model=PostResponse)
async def update_post(id: UUID, post: PostIn, user: str = Depends(authenticate),
                         session: AsyncSession = Depends(get_session)) -> PostResponse:
    await session.execute(update(Post).where(Post.id == id).values(**post.dict()))
    await session.commit()
    result = await session.get(entity=Post, ident=id)
    return result

@post_router.delete('/{id}')
async def delete_post(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
    await session.execute(delete(Post).where(Post.id == id))
    await session.commit()
    return {'message': 'Channel deleted successfully'}
