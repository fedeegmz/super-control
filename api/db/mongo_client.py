import os
# pymongo
from pymongo import MongoClient


username = os.getenv("supcon-mongouser")
password = os.getenv("supcon-mongopassw")

atlas_url = f'mongodb+srv://{username}:{password}@main.utvbo6g.mongodb.net/?retryWrites=true&w=majority'

# DATABASE #

### local ###
# db_client = MongoClient(
#     host = "localhost",
#     port = 27017
#     ).local

### remote ATLAS ###
db_client = MongoClient(
    atlas_url
    ).test