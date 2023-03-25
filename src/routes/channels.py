from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List
from sqlalchemy import insert, update, delete
from auth.authenticate import authenticate
from models.users import User
from models.channels import Channel
from schemas.channels import ChannelIn, ChannelResponse
from database.connection import get_session

channel_router = APIRouter(tags=['Channels'])

@channel_router.get('/', response_model=List[ChannelResponse])
async def get_all_channels(session: AsyncSession = Depends(get_session)) -> List[ChannelResponse]:
    results = await session.execute(select(Channel))
    return list(results.scalars().all())

@channel_router.get('/{id}', response_model=ChannelResponse)
async def get_channel(id: UUID, session: AsyncSession = Depends(get_session)) -> ChannelResponse:
    result = await session.get(entity=Channel, ident=id)
    return result

@channel_router.post('/')
async def create_channel(channel: ChannelIn, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
    user_id = await session.execute(select(User.id).where(User.username == user))
    await session.execute(insert(Channel).values(user_id=user_id.scalar(), **channel.dict()))
    await session.commit()
    return {'message': 'Channel created successfully'}

@channel_router.put('/{id}', response_model=ChannelResponse)
async def update_channel(id: UUID, channel: ChannelIn, user: str = Depends(authenticate),
                         session: AsyncSession = Depends(get_session)) -> ChannelResponse:
    result = await session.execute(select(Channel).where(Channel.user.has(User.username == user)))
    if not result.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn`t have any channels yet')
    await session.execute(update(Channel).where(Channel.id == id).values(**channel.dict()))
    await session.commit()
    result = await session.get(entity=Channel, ident=id)
    return result

@channel_router.delete('/{id}')
async def delete_channel(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(Channel).where(Channel.user.has(User.username == user)))
    if not result.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn`t have any channels yet')
    await session.execute(delete(Channel).where(Channel.id == id))
    await session.commit()
    return {'message': 'Channel deleted successfully'}
