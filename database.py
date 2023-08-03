from pymongo import MongoClient

class Database:
    mongo_db = MongoClient("mongodb://localhost:80")
    db = mongo_db["User"]
    coll = db["Data"]
    #coll = db.create_collection("Data")
    #mongo_db.drop_database("Test")
    