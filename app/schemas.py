
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class UserBase(BaseModel):
    email: EmailStr

class PostCreate(PostBase):
    pass

class Users(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: Users

    class Config:
        from_attributes = True

class PostOut(BaseModel):
    Post: Post
    votes: int

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str]=None

class Vote(BaseModel):
    post_id: int
    dir: Literal[0,1]