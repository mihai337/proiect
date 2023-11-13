from msg_broker import Rds
from database import Database
from json import loads,dumps
import requests
from models import User
from pprint import pprint
from hasher import hash
from getpass import getpass
from flask import Flask,render_template,request
from fastapi import HTTPException,status

log = False
NO_OF_TRIES = 3

app = Flask(__name__)

def process(message):
    results = Database.coll.find({"name" : message["name"]})
    for result in results:
        balance = result["balance"]
        print(result)
    
        balance = balance + message["value"]
        Database.coll.update_one({"name" : message["name"]} , {"$set" : {"balance" : balance}})
        return {"code" : "200"}
    return {"code" : "400"}

@app.post("/trans")
def transaction():
    username=request.form.get("username")
    password="a"

    payload={
        "name" : username,
        "password" : password
    }

    print(request.form)
    payload = dumps(payload)
    requests.post("http://localhost:8000/transactions" , data=payload)
    count = 0
    while 1:
        message_json = Rds.redis_conn.brpop("mod_queue" , timeout=3)
        if message_json != None:
            _,y = message_json
            message = loads(y)
            if message["name"] == username:
                count = 0
                process(message)
            else:
                count = count + 1
                Rds.redis_conn.lpush("mod_queue" , dumps(message))
                if count == 50:
                    for result in Database.coll.find({"name" : username}):
                        newbal = result["balance"]
                        print(newbal)
                    return {"code" : "200" , "modBalance" : str(newbal)}
        else:
            for result in Database.coll.find({"name" : username}):
                newbal = result["balance"]
                print(newbal)
                return {"code" : "200" , "modBalance" : str(newbal)}



@app.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    password = hash(password)

    payload = {
        "name" : username,
        "password" : password
    }
    payload = dumps(payload)

    response = requests.post("http://localhost:8000/login" , data=payload)
    if response.status_code == 200:
        results = Database.coll.find({"name" : username})
        for result in results:
            balance = result["balance"]
        print("\nLogin successfull\n")
        # print(status.HTTP_200_OK)
        # raise HTTPException(status_code=status.HTTP_200_OK)
        return {"code" : "200" , "balance" : balance}
    else:
        return {"code":"404"}

@app.post("/sign-in")
def sign_in():
    username = request.form.get("new_username")

    password = request.form.get("new_password")
    re_password = request.form.get("re_password")
    if password != re_password:
        return {"code":"400"}
    
    print(request.form)

    password = hash(password)

    payload = {
        "name" : username,
        "password" : password
    }
    payload = dumps(payload)

    response = requests.post("http://localhost:8000/sign-in" , data=payload)
    if response.status_code == 200:
        return {"code":"200"}
    else:
        return {"code":"400"}
    

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")