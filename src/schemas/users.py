from pydantic import BaseModel, EmailStr, ValidationError
from fastapi import HTTPException, status

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
