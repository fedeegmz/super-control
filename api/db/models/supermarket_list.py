from datetime import date

# typing
from typing import Optional

# pydantic
from pydantic import BaseModel, Field


class Products(BaseModel):
    description: str = Field(...)
    units: float = Field(...)
    price: float = Field(...)

class BaseSuperList(BaseModel):
    order: str = Field(...)
    issue_date: date = Field(
        ...
    )
    url: Optional[str] = Field(default=None)

class SuperList(BaseSuperList):
    username: str = Field(
        ...,
        min_length = 4,
        max_length = 15
    )
    products: list[Products] = Field()

    class Config:
        schema_extra = {
            "example": {
                "order": "0001",
                "issue_date": "2023-12-30",
                "url": "www.eticket.com",
                "username": "testuser",
                "products": [
                    {
                        "description": "Tomato",
                        "units": 1.0,
                        "price": 20.0
                    },
                    {
                        "description": "Banana",
                        "units": 3.0,
                        "price": 13.25
                    }
                ]
            }
        }