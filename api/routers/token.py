# Python
import os

from datetime import datetime, timedelta

# Typing
from typing import Annotated, Union

# FastAPI
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# JWT
from jose import jwt, JWTError

# util
from util import authenticate_user

# db
from db.deta_db import db_users

# models
from db.models.user import User, UserIn
from db.models.token import Token, TokenData


SECRET_KEY = os.getenv("JWT_SECRETKEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/login",
    responses={status.HTTP_404_NOT_FOUND: {"error": "Not Found"}}
)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        headers = {"WWW-Authenticate": "Bearer"},
        detail = {
            "errmsg": "Could not validate credentials"
        }
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    try:
        user = db_users.get(token_data.username)
        if not user:
            raise credentials_exception
    except:
        raise credentials_exception
    
    user = UserIn(**user)
    
    if user.disabled:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {
                "errmsg": "Inactive user"
            }
            )
    
    return user


### PATH OPERATIONS ###

@router.post(
        path = "/token",
        response_model = Token,
        summary = "Login a user",
        tags = ["Token"]
        )
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            headers = {"WWW-Authenticate": "Bearer"},
            detail = {
                "errmsg": "Incorrect username or password"
            }
        )
    
    access_token = create_access_token(
        data = {"sub": user.username},
        expires_delta = ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
        }


@router.get(
        path = "/users/me",
        response_model = User,
        tags = ["Token"]
        )
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user