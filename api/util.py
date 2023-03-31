# FastAPI
from fastapi import HTTPException, status

# PassLib
from passlib.context import CryptContext

# db
from db.mongo_client import db_client

# serializers
from db.serializers.user import user_serializer, users_serializer

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
    )

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def search_user_db(
        filter: dict = None,
        all: bool = False,
        num: int = 1
        ):
    try:
        if filter:
            if num == 1:
                user = db_client.users.find_one(filter)
            else:
                user = db_client.users.find(filter).to_list(num)
            
            return user_serializer(user)
        elif all:
            users = db_client.users.find()
            print(users)
            return users_serializer(users)
    except:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {"error": "User/s not found"}
        )