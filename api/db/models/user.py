# Python
from datetime import date, datetime
from typing import Optional, Union
from bson import ObjectId
# from uuid import UUID

# Pydantic
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str = Field(
        ...,
        min_length = 4,
        max_length = 15
        )
    name: str = Field(
        ...,
        min_length = 3,
        max_length = 50
        )
    lastname: str = Field(
        ...,
        min_length = 3,
        max_length = 50
        )
    email: EmailStr = Field(...)
    birth_date: Union[date, None] = Field(default=None)

class UserDB(User):
    password: str = Field(
        ...,
        min_length = 8,
        max_length = 64
        )
    
    class Config:
        schema_extra = {
            "example": {
                "username": "testuser",
                "name": "John",
                "lastname": "Doe",
                "email": "johndoe@test.com",
                "birth_date": None,
                "password": "testpassword"
            }
        }

class UserIn(UserDB):
    disabled: bool = False
    created: datetime = datetime.now()