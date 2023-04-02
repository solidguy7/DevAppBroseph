from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class HTTP_200_SUCCESS(BaseModel):
    message: str = 'User created successfully'

class HTTP_409_CONFLICT(BaseModel):
    detail: str = 'User with email provided exists already'

class HTTP_404_NOT_FOUND(BaseModel):
    detail: str = 'User with such credentials does not exist'
