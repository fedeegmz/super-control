# typing
from typing import Optional

# pydantic
from pydantic import BaseModel, Field


class _Products(BaseModel):
    name: str = Field(
        ...
    )
    description: Optional[str] = Field(
        default = None
    )
    price: float = Field(
        ...
    )
    category: Optional[str] = Field()

class SuperList(BaseModel):
    username: str = Field(
        ...,
        min_length = 4,
        max_length = 15
    )
    order: Optional[int] = Field(default=None)
    products: list[_Products] = Field()