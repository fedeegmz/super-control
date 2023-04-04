# Typing
from typing import List, Dict

# FastAPI
from fastapi import APIRouter, Path
from fastapi import HTTPException, status

# db
from db.mongo_client import db_client

# models
from db.models.supermarket_list import SuperList

router = APIRouter(
    prefix = "/super"
)


## PATH OPERATIONS ##

### Show supermarket lists ###
@router.get(
    path = "/{username}",
    status_code = status.HTTP_200_OK,
    response_model = SuperList,
    summary = "Show all supermarket lists for a user",
    tags = ["Supermarket list"]
)
async def supermarket_lists(
    username: str = Path(...)
):
    try:
        super_lists: List[Dict] = db_client.super_lists.find({"username": username})
    except:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {
                "error": "Incorrect username"
            }
        )
    
    return SuperList(**super_lists)