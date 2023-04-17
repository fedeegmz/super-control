from datetime import date

# typing
from typing import Optional

# pydantic
from pydantic import BaseModel, Field


class Products(BaseModel):
    description: Optional[str] = Field(...)
    units: float = Field(...)
    price: float = Field(...)

class SuperList(BaseModel):
    order: Optional[str] = Field(...)
    date: Optional[date] = Field(default=None)
    username: str = Field(
        ...,
        min_length = 4,
        max_length = 15
    )
    products: list[Products] = Field()