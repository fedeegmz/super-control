# Python
import os

# pymongo
from pymongo import MongoClient


username = os.getenv("DB_MONGO_USER")
password = os.getenv("DB_MONGO_PASSW")
# username = "test"
# password = "VfJWmZnNZsqbzFEw"

atlas_url = f'mongodb+srv://{username}:{password}@main.utvbo6g.mongodb.net/?retryWrites=true&w=majority'

# DATABASE #

### local ###
# db_client = MongoClient(
#     host = "localhost",
#     port = 27017
#     ).local

### remote ATLAS ###
db_client = MongoClient(atlas_url).test

users_mongo_db = db_client.users
superlist_mongo_db = db_client.super_list