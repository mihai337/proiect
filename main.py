from fastapi import FastAPI,HTTPException,status,Form
from models import User
from database import Database
from msg_broker import Rds
import random
from json import dumps


app = FastAPI()


def send_transactions(name : str , nr_msg : int):
    for i in range(nr_msg):
        value = random.randint(-20,20)
        message = {
            "name" : name,
            "value" : value
        }
        m = dumps(message)
        Rds.redis_conn.lpush("mod_queue" , m)


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
            send_transactions(user.name,5)
            raise HTTPException(status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


print(Database.mongo_db.list_database_names())