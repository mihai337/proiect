from fastapi import FastAPI,HTTPException,status,Form
from fastapi.middleware.cors import CORSMiddleware
from models import User,PartialUser
from database import Database
from msg_broker import Rds
import random
from json import dumps
import uvicorn
from hasher import hash

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    raise HTTPException(status_code=status.HTTP_200_OK)


@app.post("/sign-in")
def sign_in(user : User):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        # print("1")
        raise HTTPException(status_code=status.HTTP_302_FOUND)
    Database.coll.insert_one({"name":user.name , "password":hash(user.password) , "balance":user.balance})
    raise HTTPException(status_code=status.HTTP_200_OK)


@app.post("/login")
def login(user : User):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        if result["password"] == hash(user.password):
            balance = result["balance"]
            return {"code" : "200" , "balance" : balance}
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


@app.post("/get-balance")
def get_balance(user : PartialUser):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        balance = result["balance"]
        return {"code" : "200" , "balance" : balance}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/transfer/")
def transfer(mainUser : str , secondaryUser : PartialUser):
    if(not secondaryUser.balance.isnumeric()):
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY)
    
    mainRes = Database.coll.find({"name" : mainUser})
    mainRes = [x for x in mainRes][0]

    secRes = Database.coll.find({"name" : secondaryUser.name})
    secRes = [x for x in secRes]

    if(secRes is None or not secRes):
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    secRes = [x for x in secRes][0]

    if(mainRes['balance'] - int(secondaryUser.balance) < 0):
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    
    # print(int(secondaryUser.balance))
    Database.coll.update_one({"name" : mainUser} , {"$set" : {"balance" : mainRes['balance']-int(secondaryUser.balance)}})
    Database.coll.update_one({"name" : secondaryUser.name} , {"$set" : {"balance" : secRes['balance']+int(secondaryUser.balance)}})
    # print(mainRes)
    raise HTTPException(status_code=status.HTTP_200_OK)
      
@app.post("/addfunds")
def addfunds(user : PartialUser):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        balance = int(result["balance"])
        print(balance)
        Database.coll.update_one({"name" : user.name} , {"$set" : {"balance" : balance+int(user.balance)}})
        raise HTTPException(status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


if __name__ == "__main__":
    uvicorn.run(app="main:app" , host="0.0.0.0" , port=8000, reload=True)