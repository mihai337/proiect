from fastapi import FastAPI,HTTPException,status,Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User,PartialUser,Bill
from msg_broker import Rds
import random
from json import dumps,loads
import uvicorn
from pprint import pprint
import firebase_admin
from firebase_admin import credentials, auth, firestore

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("firebase-admin.json")
    firebase_admin.initialize_app(cred)

firestore_db = firestore.client()
auth_scheme = HTTPBearer()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#TODO : when an account is created, a user should be created in the database with a balance of 0 and a type of user

def verify_token(credentials : HTTPAuthorizationCredentials = Depends(auth_scheme)):
    # test = {
    #     "iss": "https://securetoken.google.com/ssd0-68e95",
    #     "aud": "ssd0-68e95",
    #     "auth_time": 1734565573,
    #     "user_id": "vfFQcZ5r6caXi9X9v4Dxtx8VYEI2",
    #     "sub": "vfFQcZ5r6caXi9X9v4Dxtx8VYEI2",
    #     "iat": 1734565573,
    #     "exp": 1734569173,
    #     "email": "constantinm7787@gmail.com",
    #     "email_verified": False,
    #     "firebase": {
    #         "identities": {
    #         "email": [
    #             "constantinm7787@gmail.com"
    #         ]
    #         },
    #         "sign_in_provider": "password"
    #     },
    #     "uid": "vfFQcZ5r6caXi9X9v4Dxtx8VYEI2"
    # }  

    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token, token is not a string or is empty")
    except auth.InvalidIdTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token, token is not a valid Firebase ID token")
    except auth.ExpiredIdTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token, token is expired")
    except auth.RevokedIdTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token, token is revoked")
    except auth.CertificateFetchError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token, unable to fetch the public key certificates required to verify the token")
    except auth.UserDisabledError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token, user account has been disabled")
    except auth.UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token, user account does not exist")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/")
def home():
    raise HTTPException(status_code=status.HTTP_200_OK)

@app.get("/create")
def create_user(user : dict = Depends(verify_token)):
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    print(user)
    if not doc.exists:
        doc_ref.set({
            "email" : user['email'],
            "balance" : 0,
            "history" : [],
            "type" : ["user"]
        })
        return {"status" : "User created"}
    else:
        return {"status" : "User already exists"}

@app.get("/balance")
def get_balance(user : dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    if doc.exists:
        return {"balance" : doc.to_dict()['balance']}

@app.post("/transfer") #modify this
def transfer(secondaryUser : PartialUser, user : dict = Depends(verify_token)):
    mainUser = user
    if(float(secondaryUser.balance) < 0):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    doc_ref = firestore_db.collection("users").document(mainUser['uid'])
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User found, but no data found in the database")
    mainRes = doc.to_dict()

    doc_ref = firestore_db.collection("users").document(secondaryUser.name)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User found, but no data found in the database")
    mainRes = doc.to_dict()

    if(mainRes['balance'] - float(secondaryUser.balance) < 0):
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    
    # print(int(secondaryUser.balance))
    Database.coll.update_one({"name" : mainUser} , {"$set" : {"balance" : mainRes['balance']-float(secondaryUser.balance)}})
    Database.coll.update_one({"name" : secondaryUser.name} , {"$set" : {"balance" : secRes['balance']+float(secondaryUser.balance)}})
    # print(mainRes)
    raise HTTPException(status_code=status.HTTP_200_OK)
      
@app.post("/modifyfunds")
def addfunds(user : dict = Depends(verify_token), amount : float = Form(...)):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    if doc.exists:
        user_data = doc.to_dict()
        user_data['balance'] += amount
        if amount < 0:
            user_data['history'].append({"from": "system", "to": user['uid'] , "amount" : amount , "message" : "Funds have been withdrawn"})
        else:
            user_data['history'].append({"from": "system", "to": user['uid'] , "amount" : amount , "message" : "Funds have been added"})
        doc_ref.update(user_data)
        return user_data

@app.post("/sendbill")
def sendBill(data : Bill, user : dict = Depends(verify_token)):
    if data.amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    rqueue = Rds(data.username)
    uid = random.randint(0,1000000)
    message = {
        "username" : user['uid'],
        "factName" : data.factName,
        "amount" : data.amount,
        "uid":uid
    }

    message = dumps(message)
    rqueue.redis_conn.lpush(data.username , message)
    raise HTTPException(status_code=status.HTTP_200_OK)

@app.get("/bills")
def getbills(user : dict = Depends(verify_token)):
    name = user['uid']

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

    if data == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) #handeling the case when the bill is not found
    
    rq.redis_conn.lpush(name , message)
    return data

@app.get("/paybill/{uid}")
def paybill(uid, user : dict = Depends(verify_token)):
    name = user['uid']
    rq = Rds(name=name)
    message = rq.redis_conn.rpop(name=name)
    message = loads(message.decode("ASCII"))
    uid = int(uid)
    init_uid = message['uid']

    while message['uid'] != uid and message != None:
        message = dumps(message)
        rq.redis_conn.lpush(name , message)
        message = rq.redis_conn.rpop(name=name)
        message = loads(message.decode("ASCII"))
        if init_uid == message['uid']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) #handeling the case when the bill is not found


    result_ref = firestore_db.collection("users").document(name)
    result_fact_ref = firestore_db.collection("users").document(message['factName'])

    result = result_ref.get()
    result_fact = result_fact_ref.get()

    if not result.exists or not result_fact.exists:
        rq.redis_conn.lpush(name , dumps(message))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


    if result['balance'] - float(message['amount']) < 0:
        rq.redis_conn.lpush(name , dumps(message))
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED) #handeling the case when the user does not have enough money

    result = result.to_dict()
    result_fact = result_fact.to_dict()

    result["balance"] = result["balance"] - float(message['amount'])
    result_fact["balance"] = result_fact["balance"] + float(message['amount'])

    result["history"].append({"from": name, "to": message['factName'] , "amount" : -float(message['amount']) , "message" : message['factName'] + " bill has been payed"})
    result_fact["history"].append({"from": name, "to": message['factName'] , "amount" : float(message['amount']) , "message" : message['factName'] + " bill has been payed"})

    result_ref.update(result)
    result_fact_ref.update(result_fact)

    raise HTTPException(status_code=status.HTTP_200_OK)

@app.get("/history")
def gethistory(user : dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    if not doc.exists:
        return doc.to_dict()['history']

if __name__ == "__main__":
    uvicorn.run(app="main:app" , host="0.0.0.0" , port=8000, reload=True)