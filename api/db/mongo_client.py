# Python
import os
from bson import ObjectId

# typing
from typing import Union

# FastAPI
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

# pymongo
from pymongo import MongoClient

# models
from .models.user import User, UserDB, UserIn
from .models.supermarket_list import SuperList

# serializers
from .serializers.user import users_serializer


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
        username = os.getenv("DB_MONGO_USER")
        password = os.getenv("DB_MONGO_PASSW")

        atlas_url = f'mongodb+srv://{username}:{password}@main.utvbo6g.mongodb.net/?retryWrites=true&w=majority'
        
        if test:
            self.__db_client = MongoClient(atlas_url).test
        else:
            self.__db_client = MongoClient(atlas_url).production
        
        self.users_mongo_db = self.__db_client.users
        self.superlist_mongo_db = self.__db_client.super_list
    
    # USERS #
    def get_available_users(self) -> list:
        """
        Returns all available users from the 'users' collection.

        Returns:
            list: A list containing all available users.
        """
        try:
            users = self.users_mongo_db.aggregate([
                {
                    "$match": {"disabled": False}
                },
                {
                    "$limit": 1000
                },
                {
                    "$project": {
                        "_id": 0,
                        "created": 0,
                        "disabled": 0,
                        "password": 0
                    }
                }
            ])

        except Exception as err:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "DB error: users not found",
                    "errdetail": str(err)
                }
            )
        
        return users_serializer(users)

    def get_user_with_username(
        self,
        username: str,
        full_user: bool = False
    ) -> Union[User, UserDB]:
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
            projection = {
                "_id": 0,
                "password": 0
            }
            if not full_user:
                projection["disabled"] = 0
                projection["created"] = 0
            
            user = self.users_mongo_db.find_one({"username": username}, projection)
            
            if full_user:
                user = UserDB(**user)
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
    
    def get_user_with_username_and_update(
        self,
        username: str,
        updates: list[dict]
    ) -> User:
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
            updates_dict = {{"$set": update} for update in updates}

            self.users_mongo_db.find_one_and_update(
                filter = {"username": username},
                update = updates_dict
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

    def exist_user(
        self,
        username: str
    ) -> bool:
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

    def insert_user(
        self,
        data: dict
    ) -> User:
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
                {"_id": ObjectId(inserted_id)},
                {
                    "_id": 0,
                    "password": 0,
                    "created": 0,
                    "disabled": 0
                }
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
    
    # SUPER LISTS #
    def get_available_superlist_for_user(
        self,
        username: str
    ) -> list:
        """
        Returns all available super lists for the specified user from the 'super_list' collection.

        Parameters:
            - username (str): The username of the user for whom to retrieve the super lists.

        Returns:
            list: A list containing all available super lists for the specified user.
        """
        try:
            super_list = self.superlist_mongo_db.aggregate([
                {
                    "$match": {
                        "username": username,
                        "disabled": False
                    }
                },
                {
                    "$limit": 1000
                },
                {
                    "$project": {
                        "_id": 0
                    }
                }
            ])
        except Exception as err:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "DB error: super lists not found",
                    "errdetail": str(err)
                }
            )
        
        return super_list

    def get_superlist_with_orderid(
        self,
        username: str,
        order_id: str
    ) -> SuperList:
        """
        Returns the super list with the specified order ID from the 'super_list' collection.

        Parameters:
            - order_id (str): The order ID of the super list to retrieve.

        Returns:
            dict: A dictionary representing the retrieved super list.
        """
        try:
            super_list = self.superlist_mongo_db.find_one(
                {
                    "username": username,
                    "order": order_id
                }
            )
            super_list = SuperList(**super_list)

        except Exception as err:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "DB error: super lists not found",
                    "errdetail": str(err)
                }
            )
        
        if super_list.disabled:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = {
                    "errmsg": "Supermarket list was deleted"
                }
            )
        
        return super_list
    
    def get_superlist_with_orderid_and_update(
        self,
        username: str,
        order_id: str,
        updates: list[dict]
    ) -> SuperList:
        """
        Updates the supermarket list with the specified order ID with the given updates.

        Parameters:
            - order_id (str): The order ID of the supermarket list to update.
            - updates (dict): The updates to apply to the supermarket list.

        Returns:
            dict: The updated supermarket list.

        Raises:
            HTTPException: If the supermarket list with the specified order ID does not exist, or if there is an error updating the supermarket list in the database.
        """
        if not self.exist_superlist(username=username, order_id=order_id):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = {
                    "errmsg": "Supermarket list does not exist"
                }
            )
        
        try:
            updates_dict = {{"$set": update} for update in updates}
            self.superlist_mongo_db.find_one_and_update(
                filter = {"username": username, "order": order_id},
                update = updates_dict
            )
            super_list_updated = self.get_superlist_with_orderid(order_id)

        except Exception as err:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {
                    "errmsg": "DB error: supermarket list not updated",
                    "errdetail": str(err)
                }
            )
        
        return super_list_updated

    def exist_superlist(
        self,
        username: str,
        order_id: str
    ) -> bool:
        """
        Determines whether a superlist with the specified order ID 
        exists in the 'superlist_mongo_db' collection.

        Parameters:
            - order_id (str): The order ID of the superlist to check.

        Returns:
            bool: True if the superlist exists, False otherwise.
        """
        try:
            exist = self.superlist_mongo_db.find_one(
                {
                    "username": username,
                    "order": order_id,
                    "disabled": False
                }
            )
        except:
            return False
        
        if exist:
            return True
        else:
            return False

    def insert_superlist(
        self,
        data: SuperList
    ) -> SuperList:
        """
        Inserts a new super list into the 'super_list' collection.

        Parameters:
            - data (dict): A dictionary containing the fields and values for the new super list.

        Returns:
            dict: A dictionary representing the inserted super list.
        """   
        if self.exist_superlist(data.order):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = {
                    "errmsg": "Order exists"
                }
            )
        
        try:
            inserted_id = self.superlist_mongo_db.insert_one(
                jsonable_encoder(data)
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
            super_list = SuperList(**super_list)
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