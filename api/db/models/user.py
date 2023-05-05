# Python
from datetime import date, datetime
from typing import Optional

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
        max_length = 20
        )
    lastname: str = Field(
        ...,
        min_length = 3,
        max_length = 20
        )
    email: EmailStr = Field(...)
    birth_date: Optional[date] = Field(default=None)

class UserDB(User):
    password: str = Field(
        ...,
        min_length = 8,
        max_length = 64
        )
    
    class Config:
        schema_extra = {
            "example": {
                "username": "ironman",
                "name": "Anthony",
                "lastname": "Stark",
                "email": "tony@starkindustries.com",
                "birth_date": str(date(2000, 12, 25)),
                "password": "ILoveMark40"
            }
        }

class UserIn(UserDB):
    disabled: bool = False
    created: datetime = datetime.now()