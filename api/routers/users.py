# Python

# Typing
from typing import Annotated, List

# FastAPI
from fastapi import APIRouter, Path, Query, Body
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

# util
from util import get_password_hash, authenticate_user

# db
from db.deta_db import db_users

# models
from db.models.user import User, UserDB, UserIn

# serializers
from db.serializers.user import users_serializer


router = APIRouter(
    prefix = "/users",
    responses = {status.HTTP_404_NOT_FOUND: {"error": "Not Found"}}
)


### PATH OPERATIONS ###

## register a user ##
@router.post(
    path = "/signup",
    status_code = status.HTTP_201_CREATED,
    response_model = User,
    summary = "Register a user",
    tags = ["Users"]
)
async def signup(
    user_data: UserDB = Body(...)
):
    try:
        user_data = user_data.dict()
        user_data["password"] = get_password_hash(user_data["password"])
        user_data["birth_date"] = str(user_data["birth_date"])

        user_in = db_users.get(user_data.get("username"))
        if user_in:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "Username exists",
                    "user_detail": User(**user_in)
                }
            )

        new_user = db_users.put(
            data = user_data,
            key = user_data.get("username")
        )

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "User not inserted",
                "errdetail": str(err)
                }
        )
    
    return new_user

## show users ##
@router.get(
        path = "/",
        status_code = status.HTTP_200_OK,
        response_model = list[User],
        summary = "Show all users",
        tags = ["Users"])
async def users():
    try:
        users_db = db_users.fetch({"disabled": False}).items
    except:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error"
            }
        )
    users_list = users_serializer(users_db)
    
    return users_list

## show a user ##
@router.get(
        path = "/{username}",
        status_code = status.HTTP_200_OK,
        response_model = User,
        summary = "Show a user",
        tags = ["Users"])
async def user(username: str = Path(...)):
    try:
        user_db = db_users.get(username)
        user_db = User(**user_db)
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {
                "errmsg": "User not found",
                "errdetail": str(err)
            }
            )
    
    return user_db

## update a user ##
@router.patch(
        path = "/{username}",
        status_code = status.HTTP_200_OK,
        response_model = User,
        summary = "Update a user",
        tags = ["Users"]
)
async def update_user(
    username: str = Path(...),
    user_updates: dict = Body(...)
):
    try:
        user = db_users.get(username)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = {
                    "errmsg": "User not found"
                }
            )
        
        user = UserIn(**user)

        if user.disabled:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "User has already been deleted"
                }
            )
        
        updated_user = db_users.update(
            updates = user_updates,
            key = username
        )
    except:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "error": "User not updated"
            }
        )
    
    if not updated_user:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "error": "User not updated"
            }
        )
    
    return User(**updated_user)

## delete a user ##
@router.delete(
    path = "/{username}",
    status_code = status.HTTP_200_OK,
    response_model = User,
    summary = "Delete a user",
    tags = ["Users"]
    )
async def delete_user(
    username: str = Path(...)
):
    try:
        user = db_users.get(username)
        user = UserIn(**user)

        if user.disabled:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "User has already been deleted"
                }
            )
        
        user.disabled = True
        deleted_user = db_users.put(
            data = user,
            key = user.username
        )
    except:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "error": "User not deleted"
            }
        )
    
    return User(**deleted_user)