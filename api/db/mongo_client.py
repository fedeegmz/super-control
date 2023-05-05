# Python
import os
from bson import ObjectId

# FastAPI
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

# pymongo
from pymongo import MongoClient

# models
from .models.user import User, UserIn
from .models.supermarket_list import SuperList

# serializers
from .serializers.user import users_serializer


username = os.getenv("DB_MONGO_USER")
password = os.getenv("DB_MONGO_PASSW")

atlas_url = f'mongodb+srv://{username}:{password}@main.utvbo6g.mongodb.net/?retryWrites=true&w=majority'


class MongoDB:
    """
    The MongoDB class is a Python class that provides methods for interacting with a MongoDB database.
    This class contains methods for retrieving, updating, and creating users and grocery lists.
    There are also methods for checking the existence of a user and 
    getting specific grocery lists by order number.

    The documentation for this class has been provided by ChatGPT, 
    a natural language model based on OpenAI's GPT-3.5.
    The documentation includes details on input and output parameters, 
    as well as possible exceptions that may be thrown during the execution of the methods.
    """

    def __init__(self, test: bool = False) -> None:
        """
        Initializes a MongoDB instance.

        Parameters:
            - test (bool, optional): A boolean indicating whether the MongoDB instance
            is for testing purposes. Defaults to False.
        """
        if test:
            self.__db_client = MongoClient(atlas_url).test
        else:
            self.__db_client = MongoClient(atlas_url).production
        
        self.users_mongo_db = self.__db_client.users
        self.superlist_mongo_db = self.__db_client.super_list
    
    def get_available_users(self):
        """
        Returns all available users from the 'users' collection.

        Returns:
            list: A list containing all available users.
        """
        try:
            users = self.users_mongo_db.find(
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

    def get_user_with_username(self, username: str, full_user: bool = False):
        """
        Returns a user with the specified username from the 'users' collection.

        Parameters:
            - username (str): The username of the user to retrieve.
            - full_user (bool, optional): A boolean indicating whether to retrieve the
            full user document. Defaults to False.

        Returns:
            User or UserIn: A User or UserIn instance representing the retrieved user.
        """
        try:
            user = self.users_mongo_db.find_one({"username": username})
            
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
    
    def get_user_with_username_and_update(self, username: str, updates: dict):
        """
        Updates a user with the specified username from the 'users' collection and
        returns the updated user.

        Parameters:
            - username (str): The username of the user to update.
            - updates (dict): A dictionary containing the fields to update and their
            new values.

        Returns:
            User: A User instance representing the updated user.
        """
        try:
            self.users_mongo_db.find_one_and_update(
                filter = {"username": username},
                update = updates
            )
            user_updated = self.get_user_with_username(username)
        except Exception as err:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "DB error: user not updated",
                    "errdetail": str(err)
                }
            )
        
        return user_updated

    def exist_user(self, username: str):
        """
        Determines whether a user with the specified username exists in the 'users' collection.

        Parameters:
            - username (str): The username of the user to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        try:
            value = self.users_mongo_db.find_one({"username": username})
        except:
            return False
        
        if value:
            return True
        else:
            return False

    def insert_user(self, data):
        """
        Inserts a new user into the 'users' collection.

        Parameters:
            - data (dict): A dictionary containing the fields and values for the new user.

        Returns:
            User: A User instance representing the inserted user.
        """
        try:
            inserted_id = self.users_mongo_db.insert_one(
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
            user = self.users_mongo_db.find_one(
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
    

    def get_available_superlist_for_user(self, username: str):
        """
        Returns all available super lists for the specified user from the 'super_list' collection.

        Parameters:
            - username (str): The username of the user for whom to retrieve the super lists.

        Returns:
            list: A list containing all available super lists for the specified user.
        """
        try:
            super_list = self.superlist_mongo_db.find({"username": username})
        except Exception as err:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "DB error: super lists not found",
                    "errdetail": str(err)
                }
            )
        
        return super_list

    def get_superlist_with_orderid(self, order_id: str):
        """
        Returns the super list with the specified order ID from the 'super_list' collection.

        Parameters:
            - order_id (str): The order ID of the super list to retrieve.

        Returns:
            dict: A dictionary representing the retrieved super list.
        """
        try:
            super_list = self.superlist_mongo_db.find_one({"order": order_id})
        except Exception as err:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "DB error: super lists not found",
                    "errdetail": str(err)
                }
            )
        
        return super_list

    def insert_superlist(self, data):
        """
        Inserts a new super list into the 'super_list' collection.

        Parameters:
            - data (dict): A dictionary containing the fields and values for the new super list.

        Returns:
            dict: A dictionary representing the inserted super list.
        """
        try:
            exist_super_list = db_client.get_superlist_with_orderid(data.order)
        except:
            pass
        else:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "Order exists",
                    "errdetail": jsonable_encoder(exist_super_list)
                }
            )
        
        try:
            inserted_id = self.superlist_mongo_db.insert_one(
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
            super_list = self.superlist_mongo_db.find_one(
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

db_client = MongoDB()