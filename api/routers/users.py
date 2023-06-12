# Python

# FastAPI
from fastapi import APIRouter, Path, Body
from fastapi import status, Depends
from fastapi.encoders import jsonable_encoder

# exceptions
from exceptions import HTTPError

# auth
from auth import get_password_hash, get_current_user

# db
from db.mongo_client import db_client

# models
from db.models.user import User, UserIn

# serializers
# from db.serializers.user import users_serializer


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
    user_data: UserIn = Body(...)
):
    user_data = user_data.dict()
    user_data["password"] = get_password_hash(user_data["password"])
    if user_data["birth_date"]:
        user_data["birth_date"] = str(user_data["birth_date"])
    
    if db_client.exist_user(user_data.get("username")):
        raise HTTPError().conflict(message="Username exists")
    
    new_user = db_client.insert_user(user_data)
    
    return new_user

## show users ##
@router.get(
        path = "/",
        status_code = status.HTTP_200_OK,
        response_model = list[User],
        summary = "Show all users",
        tags = ["Users"])
async def users():
    users_list = db_client.get_available_users()
    
    return users_list

## show a user ##
@router.get(
        path = "/{username}",
        status_code = status.HTTP_200_OK,
        response_model = User,
        summary = "Show a user",
        tags = ["Users"])
async def user(username: str = Path(...)):
    user_db = db_client.get_user_with_username(username)
    
    if not user_db:
        raise HTTPError().not_found(message="User not found")
    
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
    current_user: User = Depends(get_current_user),
    user_updates: list[dict] = Body(
        ...,
        example = [{"name": "Tony"}, {"lastname": "Stark"}]
    )
):
    user = db_client.get_user_with_username(
        username = current_user.username,
        full_user = True
    )
    
    if user.disabled:
        raise HTTPError().conflict(message="User has already been deleted")
    
    user_updated = db_client.get_user_with_username_and_update(
        username = current_user.username,
        updates = user_updates
    )
    
    return user_updated

## delete a user ##
@router.delete(
    path = "/{username}",
    status_code = status.HTTP_200_OK,
    response_model = User,
    summary = "Delete a user",
    tags = ["Users"]
    )
async def delete_user(
    current_user: User = Depends(get_current_user),
):
    user = db_client.get_user_with_username(
        username = current_user.username,
        full_user = True
    )
    
    if user.disabled:
        raise HTTPError().conflict(message="User has already been deleted")
    
    user_deleted = db_client.get_user_with_username_and_update(
        username = current_user.username,
        updates = [{"disabled": True}]
    )

    return user_deleted