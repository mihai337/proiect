from pymongo import MongoClient
from fastapi import FastAPI,Path,Query,HTTPException,status,Form
from typing import Optional
from pydantic import BaseModel


db_url = "mongodb://localhost:80"
mongo_db = MongoClient(db_url)

app = FastAPI()

class User(BaseModel):
    name : str
    password : str
    #id : Optional[int] = None



db = mongo_db["User"]
coll = db["Data"]
#coll = db.create_collection("Data")
#mongo_db.drop_database("Test")

@app.get("/")
def home():
    raise HTTPException(status_code=status.HTTP_200_OK)
    
@app.post("/sign-in")
def sign_in(username : str = Form(...) , password : str = Form(...)):
    results = coll.find({"name" : username})
    for result in results:
        return {"Error" : "Try a unique username"}
    coll.insert_one({"name":username , "password":password , "balance":0})


# @app.post("/login")
# def login(user : User):
#     results = coll.find({"name" : user.name})
#     for result in results:
#         if result["password"] == user.password:
#             return {"Success" : "Login Successful"}
#         return {"Error" : "Wrong Password"}
#     return {"Error" : "Username not found"}


@app.post("/login")
def login(username : str = Form(...) , password : str = Form(...)):
    results = coll.find({"name" : username})
    for result in results:
        if result["password"] == password:
            return {"Success" : "Login Successful"}
        return {"Error" : "Wrong Password"}
    return {"Error" : "Username not found"}


print(mongo_db.list_database_names())
