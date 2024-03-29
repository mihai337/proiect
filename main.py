from fastapi import FastAPI,HTTPException,status,Form
from fastapi.middleware.cors import CORSMiddleware
from models import User,PartialUser,Bill
from database import Database
from msg_broker import Rds
import random
from json import dumps,loads
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
    Database.coll.insert_one({"name":user.name , "password":hash(user.password) , "balance":user.balance , "type" : "user"})
    raise HTTPException(status_code=status.HTTP_200_OK)


@app.post("/login")
def login(user : User):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        if result["password"] == hash(user.password):
            if result["type"] == "user":
                balance = result["balance"]
                return {"code" : "200" , "balance" : balance , "type" : "user"}
            elif result["type"] == "fact":
                return {"code" : "200" , "type" : "fact"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/transactions") #not working with current version of message broker
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


@app.post("/get-balance") #ar trebui sa o fac get
def get_balance(user : PartialUser):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        balance = result["balance"]
        return {"code" : "200" , "balance" : balance}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/transfer/")
def transfer(mainUser : str , secondaryUser : PartialUser):
    # if(not secondaryUser.balance.isnumeric()):
    #     raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY)
    
    if(float(secondaryUser.balance) < 0):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    mainRes = Database.coll.find({"name" : mainUser})
    mainRes = [x for x in mainRes][0]

    secRes = Database.coll.find({"name" : secondaryUser.name})
    secRes = [x for x in secRes]

    if(secRes is None or not secRes):
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    secRes = [x for x in secRes][0]

    if(mainRes['balance'] - float(secondaryUser.balance) < 0):
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    
    # print(int(secondaryUser.balance))
    Database.coll.update_one({"name" : mainUser} , {"$set" : {"balance" : mainRes['balance']-float(secondaryUser.balance)}})
    Database.coll.update_one({"name" : secondaryUser.name} , {"$set" : {"balance" : secRes['balance']+float(secondaryUser.balance)}})
    # print(mainRes)
    raise HTTPException(status_code=status.HTTP_200_OK)
      
@app.post("/addfunds")
def addfunds(user : PartialUser):
    results = Database.coll.find({"name" : user.name})
    for result in results:
        balance = int(result["balance"])
        print(balance)
        Database.coll.update_one({"name" : user.name} , {"$set" : {"balance" : balance+float(user.balance)}})
        raise HTTPException(status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/sendbill")
def sendBill(data : Bill):
    #check is username in database
    rqueue = Rds(data.username)
    uid = random.randint(0,1000000)
    message = {
        "username" : data.username,
        "factName" : data.factName,
        "amount" : data.amount,
        "uid":uid
    }
    message = dumps(message)
    # print(message)
    rqueue.redis_conn.lpush(data.username , message)
    raise HTTPException(status_code=status.HTTP_200_OK)


@app.get("/getbills/{name}")
def getbills(name):
    first=True
    rq = Rds(name=name)
    message = rq.redis_conn.rpop(name=name)
    init_msg = message
    data=[]
    while message != None and (message != init_msg or first):
        rq.redis_conn.lpush(name , message)
        message = loads(message)
        data.append(message)
        message = rq.redis_conn.rpop(name=name)
        first = False
    rq.redis_conn.lpush(name , message)
    return data

@app.get("/paybill/{name}/{uid}") #vedem daca merge
def paybill(name ,uid):
    rq = Rds(name=name)
    message = rq.redis_conn.rpop(name=name)
    while message['uid'] != uid:
        rq.redis_conn.lpush(name , message)
        message = rq.redis_conn.rpop(name=name)
    results = Database.coll.find({"name" : message['username']})
    for result in results:
        fact = {
            "name":message['factName'],
            "bakance":message['amount']
        }
        transfer(message['username'] , fact)
    raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY)

if __name__ == "__main__":
    uvicorn.run(app="main:app" , host="0.0.0.0" , port=8000, reload=True)