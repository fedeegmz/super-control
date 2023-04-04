from bson.objectid import ObjectId

# Typing
from typing import List, Dict

# FastAPI
from fastapi import APIRouter, Path, Body
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
    # response_model = list[SuperList],
    summary = "Show all supermarket lists for a user",
    tags = ["Supermarket list"]
)
async def supermarket_lists(
    username: str = Path(...)
):
    try:
        super_lists = db_client.super_lists.find({"username": username})
    except:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {
                "error": "Incorrect username"
            }
        )
    
    return super_lists

### Register a supermarket list ###
@router.post(
    path = "/",
    status_code = status.HTTP_201_CREATED,
    response_model = SuperList,
    summary = "Register a supermarket list",
    tags = ["Supermarket list"]
)
async def supermarket_list(
    products: SuperList = Body(...)
):
    try:
        inserted_id = db_client.super_lists.insert_one(products.dict()).inserted_id
        products_inserted = db_client.super_lists.find_one({"_id": ObjectId(inserted_id)})
    except Exception as error:
        print(f'Error: {error}')
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "error": "List not inserted"
            }
        )
    
    return SuperList(**products_inserted)