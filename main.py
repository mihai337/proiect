from pymongo import MongoClient
from fastapi import FastAPI


db_url = "mongodb://localhost:80"
mongo_db = MongoClient(db_url)


db = mongo_db["Test"]
coll = db.create_collection("TestColl")

def search(email):
    a=5


print(mongo_db.list_database_names())
