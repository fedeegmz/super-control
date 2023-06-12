# Python

# FastAPI
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

# auth
from auth import create_access_token, authenticate_user, get_current_user

# models
from db.models.user import User
from db.models.token import Token


ACCESS_TOKEN_EXPIRE_MINUTES = 20

router = APIRouter(
    prefix="/login",
    responses={status.HTTP_404_NOT_FOUND: {"error": "Not Found"}}
)


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
    print("En read_users_me")
    return current_user