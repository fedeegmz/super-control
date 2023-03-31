# Python
import os
from datetime import datetime, timedelta

# Typing
from typing import Annotated, Union

# FastAPI
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# JWT
from jose import jwt, JWTError

# util
from util import verify_password, get_password_hash

# db
from db.mongo_client import db_client

# models
from db.models.user import User, UserDB
from db.models.token import Token, TokenData



SECRET_KEY = os.environ.get("SUPERCONTROL_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/login",
    responses={404: {"message": "Not Found"}}
)


def authenticate_user(username: str, password: str):
    try:
        user = db_client.users.find_one({"username": username})
    except Exception as err:
        print(f'DB error: {err}')
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"error": "Username not found"}
        )
    
    if not user:
        return False
    
    user = UserDB(**user)
    
    if not verify_password(password, user.password):
        return False
    
    del user.password
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
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
        user = db_client.users.find_one({"username": token_data.username})
    except:
        raise credentials_exception
    
    user = User(**user)

    if user.disabled:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Inactive user"
            )
    
    return user


### PATH OPERATIONS ###

@router.post(
        path = "/token",
        response_model = Token,
        summary = "Login a user",
        tags = ["Token"]
        )
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": user.username},
        expires_delta = ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
        }


@router.get(
        path = "/users/me/",
        response_model = User,
        tags = ["Token"]
        )
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user