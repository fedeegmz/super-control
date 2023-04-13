# FastAPI
from fastapi import HTTPException, status

# PassLib
from passlib.context import CryptContext

# db
from db.deta_db import db_users

# models
from db.models.user import User, UserDB, UserIn

# serializers
from db.serializers.user import users_serializer

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
    )

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    try:
        user = db_users.get(username)
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {
                "errmsg": "DB error",
                "errdetail": str(err)
            }
        )
    
    if not user:
        return False
    
    user = UserDB(**user)
    
    if not verify_password(password, user.password):
        return False
    
    del user.password

    return User(**user)