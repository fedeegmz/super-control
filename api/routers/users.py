# Python
from bson.objectid import ObjectId

# Typing
from typing import Annotated

# FastAPI
from fastapi import APIRouter, Path, Query, Body
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

# util
from util import get_password_hash, authenticate_user

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
        user_data = user_data.dict()
        user_data["password"] = get_password_hash(user_data["password"])
        user_in = UserDB(**user_data).dict()
        user_in["birth_date"] = str(user_data["birth_date"])

        user_id = db_client.users.insert_one(user_in).inserted_id

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

## show users ##
@router.get(
        path = "/",
        status_code = status.HTTP_200_OK,
        summary = "Show all users",
        tags = ["Users"])
async def users(
    limit: int = Query(default=None)
):
    if limit:
        users_db = db_client.users.find({"disabled": False})
    else:
        users_db = db_client.users.find({"disabled": False}).to_list(limit)
    users_list = users_serializer(users_db)

    return {
        "users": users_list
    }

## show a user ##
@router.get(
        path = "/{username}",
        status_code = status.HTTP_200_OK,
        summary = "Show a user",
        tags = ["Users"])
async def user(username: str = Path(...)):
    try:
        user_db = db_client.users.find_one({"username": username})
        user_db = User(**user_db)
    except Exception as err:
        print(f'Find error: {err}')
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User not found"
            )
    
    return {
        "user": user_db
    }

## delete a user ##
@router.delete(
    path = "/",
    status_code = status.HTTP_200_OK,
    summary = "Delete a user",
    tags = ["Users"]
    )
async def delete_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    
    try:
        db_user = db_client.users.find_one({"username": form_data.username})

        if db_user.disabled:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "error": "User has already been deleted"
                }
            )
        db_user.disabled = True
    except:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "error": "User not deleted"
            }
        )
    
    return {
        "message": "User deleted",
        "user": user
    }