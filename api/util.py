# FastAPI
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from bson import ObjectId

# db
from db.mongo_client import users_mongo_db, superlist_mongo_db

# models
from db.models.user import User, UserIn
from db.models.supermarket_list import SuperList

# serializers
from db.serializers.user import users_serializer


# USERS #

def get_available_users():
    try:
        users = users_mongo_db.find(
            {"disabled": False}
        )
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: users not found",
                "errdetail": str(err)
            }
        )
    
    return users_serializer(users)

def get_user_with_username(username: str, full_user: bool = False):
    try:
        user = users_mongo_db.find_one({"username": username})
        
        if full_user:
            user = UserIn(**user)
            del user.password
        else:
            user = User(**user)
    
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: user not found",
                "errdetail": str(err)
            }
        )
    
    return user

def exist_user(username: str):
    try:
        value = users_mongo_db.find_one({"username": username})
    except:
        return False
    
    if value:
        return True
    else:
        return False

def insert_user(data):
    try:
        inserted_id = users_mongo_db.insert_one(
            jsonable_encoder(UserIn(**data))
        ).inserted_id
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: user not inserted",
                "errdetail": str(err)
            }
        )
    
    try:
        user = users_mongo_db.find_one(
            {"_id": ObjectId(inserted_id)}
        )
        user = User(**user)
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: user not found",
                "errdetail": str(err)
            }
        )
    
    return user


# SUPER LIST #
def get_available_superlist_for_user(username: str):
    try:
        super_list = superlist_mongo_db.find({"username": username})
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: super lists not found",
                "errdetail": str(err)
            }
        )
    
    return super_list

def get_superlist_with_orderid(order_id: str):
    try:
        super_list = superlist_mongo_db.find_one({"order": order_id})
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: super lists not found",
                "errdetail": str(err)
            }
        )
    
    return super_list

def insert_superlist(data):
    try:
        inserted_id = superlist_mongo_db.insert_one(
            jsonable_encoder(SuperList(**data))
        ).inserted_id
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: super list not inserted",
                "errdetail": str(err)
            }
        )
    
    try:
        super_list = superlist_mongo_db.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error: super list not found",
                "errdetail": str(err)
            }
        )
    
    return super_list