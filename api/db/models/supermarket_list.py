# typing
from typing import Optional

# pydantic
from pydantic import BaseModel, Field

class SuperList(BaseModel):
    username: str = Field(
        ...,
        min_length = 4,
        max_length = 15
    )
    order: Optional[int] = Field(default=None)
    super_list: dict = Field(default={})