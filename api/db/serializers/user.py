# FastAPI
from fastapi.encoders import jsonable_encoder

# models
from db.models.user import User, UserDB

def user_serializer(user) -> dict:
    try:
        return {
            "_id": str(user["_id"]),
            "username": user["username"],
            "name": user["name"],
            "lastname": user["lastname"],
            # "email": user["email"],
            # "birth_date": str(user.get("birth_date")),
            # "created": str(user.get("created"))
        }
    except Exception as err:
        print(f'Serializer error: {err}')

def user_db_serializer(user) -> dict:
    try:
        user["_id"] = str(user["_id"])

        return jsonable_encoder(user)
    except Exception as err:
        print(f'Serializer error: {err}')

def users_serializer(users) -> list[dict]:
    return [user_serializer(user) for user in users]