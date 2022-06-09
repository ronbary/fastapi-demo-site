from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint


# create user model


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# we want to create out schema Class
# based on BaseModel from pydantic
# The schema will look like this:

# title str , content str , category

# The schema Class for our model class to post data to the server
# this enforce strict schema to send what is needed to the server for response and request
# class Post(BaseModel):
# title: str
# content: str
# published: bool = True  # add an optional value with default as True

# rating: Optional[int] = None  # add optional value for integer the default is None (import from typing package)


# using inheritance make sense to represent each of the requests POST / CREATE / UPDATE ...


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True  # add an optional value with default as True


class PostCreate(PostBase):
    pass


# define what to return as a response
###############################################
# create class for the response schema
# The Post inherits from PostBase , these will be the fields we return as a response

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)  # value less than 1
