# Python
from bson.objectid import ObjectId

# FastAPI
from fastapi import APIRouter, Path, Body
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

# util
from util import get_password_hash

# db
from db.mongo_client import db_client

# models
from db.models.user import User, UserDB

# serializers
from db.serializers.user import users_serializer


router = APIRouter(
    prefix = "/users",
    responses = {status.HTTP_404_NOT_FOUND: {"message": "Not Found"}}
)


### PATH OPERATIONS ###

## show users ##
@router.get(
        path = "/",
        summary = "Show all users",
        tags = ["Users"])
async def users():
    users_db = db_client.users.find()
    users_db = users_serializer(users_db)

    return {
        "users": users_db
    }

## show a user ##
@router.get(
        path = "/{user_id}",
        status_code = status.HTTP_200_OK,
        summary = "Show a user",
        tags = ["Users"])
async def user(user_id: str = Path(...)):
    try:
        user_db = db_client.users.find_one({"_id": ObjectId(user_id)})
    except Exception as err:
        print(f'Find error: {err}')
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User not found"
            )
    user_db = User(**user_db)
    
    return {
        "user": user_db
    }

## register a user ##
@router.post(
    path = "/signup",
    status_code = status.HTTP_201_CREATED,
    summary = "Register a user",
    tags = ["Users"]
)
async def signup(
    user_data: UserDB = Body(...)
):
    try:
        user_data = jsonable_encoder(user_data)
        user_data["password"] = get_password_hash(user_data["password"])
        user_id = db_client.users.insert_one(user_data).inserted_id

    except Exception as err:
        print(f'Error: {err}')
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = {
                "error": "User not inserted"
                }
        )
    
    new_user = db_client.users.find_one({"_id": ObjectId(user_id)})
    new_user = User(**new_user)
    
    return {
        "message": "User inserted",
        "user": new_user
        }