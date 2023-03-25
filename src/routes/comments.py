from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List
from sqlalchemy import insert, update, delete
from auth.authenticate import authenticate
from models.users import User
from models.comments import Comment
from schemas.comments import CommentUpdate, CommentIn, CommentResponse
from database.connection import get_session

comment_router = APIRouter(tags=['Comments'])

@comment_router.get('/', response_model=List[CommentResponse])
async def get_all_comments(session: AsyncSession = Depends(get_session)) -> List[CommentResponse]:
    results = await session.execute(select(Comment))
    return list(results.scalars().all())

@comment_router.get('/{id}', response_model=CommentResponse)
async def get_comment(id: UUID, session: AsyncSession = Depends(get_session)) -> CommentResponse:
    result = await session.get(entity=Comment, ident=id)
    return result

@comment_router.post('/')
async def create_comment(comment: CommentIn, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
    user_id = await session.execute(select(User.id).where(User.username == user))
    await session.execute(insert(Comment).values(user_id=user_id.scalar(), **comment.dict()))
    await session.commit()
    return {'message': 'Comment created successfully'}

@comment_router.put('/{id}', response_model=CommentResponse)
async def update_channel(id: UUID, comment: CommentUpdate, user: str = Depends(authenticate),
                         session: AsyncSession = Depends(get_session)) -> CommentResponse:
    result = await session.execute(select(Comment).where(Comment.user.has(User.username == user)))
    if not result.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn`t have such a comment')
    await session.execute(update(Comment).where(Comment.id == id).values(**comment.dict()))
    await session.commit()
    result = await session.get(entity=Comment, ident=id)
    return result

@comment_router.delete('/{id}')
async def delete_channel(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(Comment).where(Comment.user.has(User.username == user)))
    if not result.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn`t have such a comment')
    await session.execute(delete(Comment).where(Comment.id == id))
    await session.commit()
    return {'message': 'Comment deleted successfully'}
