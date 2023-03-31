# Python
from datetime import date, datetime
from typing import Optional, Union
from bson import ObjectId
# from uuid import UUID

# Pydantic
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    _id: Optional[str] = Field(...)
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
    # email: str = Field(...)
    # birth_date: Optional[date] = Field(default=None)
    # created: date = Field(default=datetime.now())
    disabled: bool = False

class UserDB(User):
    password: str = Field(
        ...,
        min_length = 8,
        max_length = 64
        )