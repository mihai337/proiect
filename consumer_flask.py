from msg_broker import Rds
from database import Database
from json import loads,dumps
import requests
from models import User
from pprint import pprint
from hasher import hash
from getpass import getpass
from flask import Flask,render_template,request,send_from_directory
from fastapi import HTTPException,status
import os

log = False
NO_OF_TRIES = 3

app = Flask(__name__ )
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "scripts")

def process(message):
    results = Database.coll.find({"name" : message["name"]})
    for result in results:
        balance = result["balance"]
        print(result)
    
        balance = balance + message["value"]
        Database.coll.update_one({"name" : message["name"]} , {"$set" : {"balance" : balance}})
        return {"code" : "200"}
    return {"code" : "400"}

@app.post("/trans") #not working with current version of message broker
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


@app.get("/index/<data>")
def index(data : str):
    if data == "user":
        return render_template("proiect.html")
    elif data == "fact":
        return render_template("facturier.html")
    

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sign-in")
def sign_in():
    return render_template("signin.html")

@app.route("/scripts")
def getScript():
    return send_from_directory(root,"script.js")
    

@app.route("/")
def home():
    return render_template("welcome.html")


if __name__ == "__main__":
    print(root)
    app.run(host="0.0.0.0" , debug=True)