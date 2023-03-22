from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
