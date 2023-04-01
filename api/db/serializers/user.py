# FastAPI
from fastapi.encoders import jsonable_encoder

# models
from db.models.user import User, UserDB, UserIn


def user_serializer(user: dict) -> User:
    user["_id"] = str(user["_id"])
    return user

def users_serializer(users: list) -> list[User]:
    return [User(**user) for user in users]

def users_in_serializer(users: list) -> list[UserIn]:
    return [UserIn(**user) for user in users]

def users_db_serializer(users: list) -> list[User]:
    return [UserDB(**user) for user in users]