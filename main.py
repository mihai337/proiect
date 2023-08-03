from fastapi import FastAPI,Path,Query,HTTPException,status,Form
from models import User
from database import Database

app = FastAPI()

@app.get("/")
def home():
    raise HTTPException(status_code=status.HTTP_200_OK)


@app.post("/sign-in")
def sign_in(username : str = Form(...) , password : str = Form(...)):
    results = Database.coll.find({"name" : username})
    for result in results:
        return {"Error" : "Try a unique username"}
    Database.coll.insert_one({"name":username , "password":password , "balance":0})


@app.post("/login")
def login(username : str = Form(...) , password : str = Form(...)):
    results = Database.coll.find({"name" : username})
    for result in results:
        if result["password"] == password:
            return {"Success" : "Login Successful"}
        return {"Error" : "Wrong Password"}
    return {"Error" : "Username not found"}


print(Database.mongo_db.list_database_names())

# @app.post("/login")
# def login(user : User):
#     results = coll.find({"name" : user.name})
#     for result in results:
#         if result["password"] == user.password:
#             return {"Success" : "Login Successful"}
#         return {"Error" : "Wrong Password"}
#     return {"Error" : "Username not found"}