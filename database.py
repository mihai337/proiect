from pymongo import MongoClient

class Database:
    mongo_db = MongoClient("mongodb://127.0.0.1:27017")
    db = mongo_db["User"]
    coll = db["Data"]
    history = db["History"]
    