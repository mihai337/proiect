from pymongo import MongoClient

class Database:
    mongo_db = MongoClient("mongodb://localhost:80")
    db = mongo_db["User"]
    coll = db["Data"]
    