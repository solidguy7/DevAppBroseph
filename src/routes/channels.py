from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from sqlalchemy import select, insert, update, delete, exists
from auth.authenticate import authenticate
from models.users import User, user_channel
from models.channels import Channel
from schemas.channels import ChannelIn, ChannelResponse
from database.connection import Settings

settings = Settings()

channel_router = APIRouter(tags=['Channels'])

@channel_router.get('/', response_model=List[ChannelResponse])
async def get_all_channels(session: AsyncSession = Depends(settings.get_session)) -> List[ChannelResponse]:
    results = await session.execute(select(Channel))
    return list(results.scalars().all())

@channel_router.get('/{id}', response_model=ChannelResponse)
async def get_channel(id: UUID, session: AsyncSession = Depends(settings.get_session)) -> ChannelResponse:
    result = await session.get(entity=Channel, ident=id)
    return result

@channel_router.post('/')
async def create_channel(channel: ChannelIn, user: str = Depends(authenticate), session: AsyncSession = Depends(
    settings.get_session)) -> dict:
    user_id = await session.execute(select(User.id).where(User.username == user))
    await session.execute(insert(Channel).values(user_id=user_id.scalar(), **channel.dict()))
    await session.commit()
    return {'message': 'Channel created successfully'}

@channel_router.post('/follow/{id}')
async def follow(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(
    settings.get_session)) -> dict:
    user_id = await session.execute(select(User.id).where(User.username == user))
    user_id = user_id.scalar()
    user_channel_id = await session.execute(select(Channel.user_id).where(Channel.id == id))
    if user_id == user_channel_id.scalar():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='You can`t follow your channels')
    check = await session.execute(select(exists().where(user_channel.c.user_id == user_id).where(user_channel.c.channel_id == id)))
    if check.scalar():
        await session.execute(delete(user_channel).where(user_channel.c.user_id == user_id).where(user_channel.c.channel_id == id))
        await session.commit()
        return {'message': 'You unfollowed this channel successfully'}
    await session.execute(insert(user_channel).values(user_id=user_id, channel_id=id))
    await session.commit()
    return {'message': 'You followed this channel successfully'}

@channel_router.put('/{id}', response_model=ChannelResponse)
async def update_channel(id: UUID, channel: ChannelIn, user: str = Depends(authenticate),
                         session: AsyncSession = Depends(settings.get_session)) -> ChannelResponse:
    channel_user_id = await session.execute(select(Channel.user_id).where(Channel.id == id))
    user_id = await session.execute(select(User.id).where(User.username == user))
    if channel_user_id.scalar() != user_id.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn`t have such a channel')
    await session.execute(update(Channel).where(Channel.id == id).values(**channel.dict()))
    await session.commit()
    result = await session.get(entity=Channel, ident=id)
    return result

@channel_router.delete('/{id}')
async def delete_channel(id: UUID, user: str = Depends(authenticate), session: AsyncSession = Depends(
    settings.get_session)) -> dict:
    channel_user_id = await session.execute(select(Channel.user_id).where(Channel.id == id))
    user_id = await session.execute(select(User.id).where(User.username == user))
    if channel_user_id.scalar() != user_id.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User doesn`t have such a channel')
    await session.execute(delete(Channel).where(Channel.id == id))
    await session.commit()
    return {'message': 'Channel deleted successfully'}
