from fastapi import FastAPI,HTTPException,status,Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User,TransferRequest,Bill
from msg_broker import Rds
import random
from json import dumps,loads
import uvicorn
from pprint import pprint
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

try:
    firebase_admin.get_app()
except ValueError:
    ON_HEROKU = os.environ.get('ON_HEROKU')
    if ON_HEROKU == "True":
        print("INFO:     Running on Heroku")
        type = os.environ.get('TYPE')
        project_id = os.environ.get('PROJECT_ID')
        private_key_id = os.environ.get('PRIVATE_KEY_ID')
        private_key = os.environ.get('PRIVATE_KEY')
        client_email = os.environ.get('CLIENT_EMAIL')
        client_id = os.environ.get('CLIENT_ID')
        auth_uri = os.environ.get('AUTH_URI')
        token_uri = os.environ.get('TOKEN_URI')
        auth_provider_x509_cert_url = os.environ.get('AUTH_PROVIDER_X509_CERT_URL')
        client_x509_cert_url = os.environ.get('CLIENT_X509_CERT_URL')
        universe_domain = os.environ.get('UNIVERSE_DOMAIN')

        cred = credentials.Certificate({
            "type": type,
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "client_id": client_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
            "client_x509_cert_url": client_x509_cert_url
        })
    else:
        print("INFO:     Running locally")
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

@app.get("/whoami")
def whoami(user : dict = Depends(verify_token)):
    return user

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

@app.post("/transfer")
def transfer(transferDetails : TransferRequest, user : dict = Depends(verify_token)):

    if user['email'] == transferDetails.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot send money to yourself")

    if(transferDetails.amount < 0):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You cannot send a negative amount of money")
    
    user_ref = firestore_db.collection("users").document(user['uid'])
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User found, but no data found in the database")
    user_res = user_doc.to_dict()

    transferUser = auth.get_user_by_email(transferDetails.email)
    transferUserId = transferUser.uid

    transferUserDocRef = firestore_db.collection("users").document(transferUserId)
    transferUserDoc = transferUserDocRef.get()
    if not transferUserDoc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User found, but no data found in the database")
    transferUserRes = transferUserDoc.to_dict()

    if(user_res['balance'] - transferDetails.amount < 0):
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Insufficient funds")
    
    user_res["balance"] = user_res["balance"] - transferDetails.amount
    user_res["history"].append({"from": user['uid'], "to": transferUserId , "amount" : -transferDetails.amount , "message" : "Money has been sent to " + transferDetails.email})

    transferUserRes["balance"] = transferUserRes["balance"] + transferDetails.amount
    transferUserRes["history"].append({"from": user['uid'], "to": transferUserId , "amount" : transferDetails.amount , "message" : "Money has been received from " + user['email']})
    
    user_ref.update(user_res)
    transferUserDocRef.update(transferUserRes)
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

@app.post("/sendbill") #fix sending bill to yourself
def sendBill(data : Bill, user : dict = Depends(verify_token)):
    if data.amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    userDocRef = firestore_db.collection("users").document(user['uid'])
    userDoc = userDocRef.get()
    if not userDoc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User found, but no data found in the database")
    userData = userDoc.to_dict()

    if "fact" not in userData['type']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to send bills")
    
    recipientAuth = auth.get_user_by_email(data.recipient)
    recipientId = recipientAuth.uid

    
    rqueue = Rds(name=recipientId)
    uid = random.randint(0,1000000)
    message = {
        "username" : user['uid'],
        "recipient" : data.recipient,
        "amount" : data.amount,
        "uid":uid
    }

    message = dumps(message)
    rqueue.redis_conn.lpush(recipientId , message)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bills found") #handeling the case when the bill is not found
    
    rq.redis_conn.lpush(name , message)
    return data

@app.get("/paybill/{uid}")
def paybill(uid : int, user : dict = Depends(verify_token)):
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
        
    try:
        recipientDetails = auth.get_user_by_email(message['recipient'])

        result_ref = firestore_db.collection("users").document(name)
        result_fact_ref = firestore_db.collection("users").document(recipientDetails.uid)

        result = result_ref.get()
        result_fact = result_fact_ref.get()

        if not result.exists or not result_fact.exists:
            rq.redis_conn.lpush(name , dumps(message))
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        result = result.to_dict()
        result_fact = result_fact.to_dict()

        if result['balance'] - float(message['amount']) < 0:
            rq.redis_conn.lpush(name , dumps(message))
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

        result["balance"] = result["balance"] - float(message['amount'])
        result_fact["balance"] = result_fact["balance"] + float(message['amount'])

        result["history"].append({"from": name, "to": message['recipient'] , "amount" : -float(message['amount']) , "message" : message['recipient'] + " bill has been payed"})
        result_fact["history"].append({"from": name, "to": message['recipient'] , "amount" : float(message['amount']) , "message" : message['recipient'] + " bill has been payed"})

        result_ref.update(result)
        result_fact_ref.update(result_fact)

        raise HTTPException(status_code=status.HTTP_200_OK)
    except Exception as e:
        rq.redis_conn.lpush(name , dumps(message))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/history")
def gethistory(user : dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    doc_ref = firestore_db.collection("users").document(user['uid'])
    doc = doc_ref.get()
    if not doc.exists:
        return doc.to_dict()['history']

# if __name__ == "__main__":
#     uvicorn.run(app="main:app" , host="0.0.0.0" , port=8000, reload=True)