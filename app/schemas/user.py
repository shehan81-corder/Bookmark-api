from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class Config:
    from_attributes = True


class TokenResponse(BaseModel):
    user: UserResponse
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
