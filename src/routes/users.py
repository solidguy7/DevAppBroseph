from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, or_
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from models.users import User
from schemas.users import UserIn, TokenResponse, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_200_SUCCESS
from database.connection import get_session

hash_password = HashPassword()

user_router = APIRouter(tags=['Users'])

@user_router.post('/signup', response_model=HTTP_200_SUCCESS,
                  responses={status.HTTP_409_CONFLICT: {'model': HTTP_409_CONFLICT}})
async def sign_user_up(user: UserIn, session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(User).where(or_(User.email == user.email, User.username == user.username)))
    user_exist = result.first()
    if user_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with email provided exists already.')
    hashed_password = hash_password.create_hash(user.password)
    new_user = user.dict()
    new_user['password'] = hashed_password
    await session.execute(insert(User).values(**new_user))
    await session.commit()
    return {'message': 'User created successfully'}

@user_router.post('/signin', response_model=TokenResponse,
                  responses={status.HTTP_404_NOT_FOUND: {'model': HTTP_404_NOT_FOUND}})
async def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(
    get_session)) -> dict:
    result = await session.execute(select(User).where(User.username == user.username))
    user_exist = result.scalar()
    if user_exist and hash_password.verify_hash(user.password, user_exist.password):
        access_token = create_access_token(user_exist.username)
        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User with such credentials does not exist')
