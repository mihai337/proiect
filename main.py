from fastapi import FastAPI,HTTPException,status,Form, Header
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#TODO : when an account is created, a user should be created in the database with a balance of 0 and a type of user

def verify_token(token):
    # {
    #     "iss": "https://securetoken.google.com/ssd0-68e95",
    #     "aud": "ssd0-68e95",
    #     "auth_time": 1734565573,
    #     "user_id": "vfFQcZ5r6caXi9X9v4Dxtx8VYEI2",
    #     "sub": "vfFQcZ5r6caXi9X9v4Dxtx8VYEI2",
    #     "iat": 1734565573,
    #     "exp": 1734569173,
    #     "email": "constantinm7787@gmail.com",
    #     "email_verified": false,
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

@app.get("/balance")
def get_balance(authorization : str = Header(None)):
    user = verify_token(authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    if doc.exists:
        return {"balance" : doc.to_dict()['balance']}

@app.post("/transfer")
def transfer(secondaryUser : PartialUser, authorization : str = Header(None)):
    mainUser = verify_token(authorization)
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
      
@app.post("/addfunds")
def addfunds(authorization : str = Header(None), amount : float = Form(...)):
    user = verify_token(authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    if doc.exists:
        user_data = doc.to_dict()
        user_data['balance'] += amount
        doc_ref.update(user_data)
        return user_data

@app.post("/sendbill")
def sendBill(data : Bill, authorization : str = Header(None)):
    user = verify_token(authorization)
    
    if data.amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    rqueue = Rds(data.username)
    uid = random.randint(0,1000000)
    message = {
        "username" : data.username,
        "factName" : data.factName,
        "amount" : data.amount,
        "uid":uid
    }

    message = dumps(message)
    rqueue.redis_conn.lpush(data.username , message)
    raise HTTPException(status_code=status.HTTP_200_OK)

@app.get("/bills")
def getbills(authorization : str = Header(None)):
    user = verify_token(authorization)
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
def paybill(uid, authorization : str = Header(None)):
    user = verify_token(authorization)
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


    result = Database.coll.find({"name" : name})
    result = [x for x in result][0]
    result_fact = Database.coll.find({"name" : message['factName']})
    result_fact = [x for x in result_fact][0]
    if result is None or result_fact is None:
        rq.redis_conn.lpush(name , dumps(message))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


    if result['balance'] - float(message['amount']) < 0:
        rq.redis_conn.lpush(name , dumps(message))
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED) #handeling the case when the user does not have enough money

    Database.coll.update_one({"name" : name} , {"$set" : {"balance" : result['balance']-float(message['amount'])}})
    Database.coll.update_one({"name" : message['factName']} , {"$set" : {"balance" : result_fact['balance']+float(message['amount'])}})

    Database.history.insert_one({"from" : name , "to" : message['factName'] , "amount" : message['amount'] , "message" : message['factName'] + " bill has been payed"})
    raise HTTPException(status_code=status.HTTP_200_OK)

@app.get("/history")
def gethistory(authorization : str = Header(None)):
    user = verify_token(authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    if not doc.exists:
        return doc.to_dict()['history']

if __name__ == "__main__":
    uvicorn.run(app="main:app" , host="0.0.0.0" , port=8000, reload=True)