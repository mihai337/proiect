from fastapi import FastAPI,HTTPException,status,Form
from models import User
from database import Database
from msg_broker import Rds
import random
from json import dumps

app = FastAPI()


@app.get("/")
def home():
    raise HTTPException(status_code=status.HTTP_200_OK)


@app.post("/sign-in")
def sign_in(user : User):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        raise HTTPException(status_code=status.HTTP_302_FOUND)
    Database.coll.insert_one({"name":user.name , "password":user.password , "balance":user.balance})
    raise HTTPException(status_code=status.HTTP_200_OK)


@app.post("/login")
def login(user : User):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        if result["password"] == user.password:
            raise HTTPException(status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/transactions")
def send(user : User):
    for i in range(5):
        value = random.randint(-20,20)
        results = Database.coll.find({"name" : user.name})
        for result in results:
            if result["balance"] + value < 0:
                value = -value
            message = {
                "name" : user.name,
                "value" : value
            }
            mjson = dumps(message)
            Rds.redis_conn.lpush("mod_queue" , mjson)

# print(Database.mongo_db.list_database_names())