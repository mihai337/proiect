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
def sign_in(username : str = Form(...) , password : str = Form(...) , balance : float = Form(...)):
    results = Database.coll.find({"name" : username})
    for result in results:
        return {"Error" : "Try a unique username"}
    Database.coll.insert_one({"name":username , "password":password , "balance":balance})


@app.post("/login")
def login(username : str = Form(...) , password : str = Form(...)):
    results = Database.coll.find({"name" : username})
    for result in results:
        if result["password"] == password:
            send_transactions(username,1)
            return {"Username" : username , "Balance" : result["balance"]}
        return {"Error" : "Wrong Password"}
    return {"Error" : "Username not found"}


print(Database.mongo_db.list_database_names())