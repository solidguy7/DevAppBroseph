from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from models.users import User
from schemas.users import UserIn, TokenResponse
from database.connection import Settings

settings = Settings()

hash_password = HashPassword()

user_router = APIRouter(tags=['Users'])

@user_router.post('/signup')
async def sign_user_up(user: UserIn, session: AsyncSession = Depends(settings.get_session)) -> dict:
    result = await session.execute(select(User).where(User.email == user.email))
    user_exist = result.first()
    if user_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with email provided exists already.')
    hashed_password = hash_password.create_hash(user.password)
    new_user = user.dict()
    new_user['password'] = hashed_password
    await session.execute(insert(User).values(**new_user))
    await session.commit()
    return {'message': 'User created successfully'}

@user_router.post('/signin', response_model=TokenResponse)
async def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(
    settings.get_session)) -> dict:
    result = await session.execute(select(User).where(User.username == user.username))
    user_exist = result.scalar()
    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    if hash_password.verify_hash(user.password, user_exist.password):
        access_token = create_access_token(user_exist.username)
        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid details passed')
