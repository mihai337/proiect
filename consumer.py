from msg_broker import Rds
from database import Database
from json import loads,dumps
import requests
from models import User
from pprint import pprint
from hasher import hash

log = False
NO_OF_TRIES = 3

def process(message):
    results = Database.coll.find({"name" : message["name"]})
    for result in results:
        balance = result["balance"]
        print(result)
    
        balance = balance + message["value"]
        Database.coll.update_one({"name" : message["name"]} , {"$set" : {"balance" : balance}})
        return {"Update" : "Successful"}
    return {"Error" : "Not found"}

def transaction():

    choice = input("\nDo you want to complete all transactions?y/n\n")

    if choice == "y":
        payload={
            "name" : username,
            "password" : password
        }
        payload = dumps(payload)
        requests.post("http://localhost:8000/transactions" , data=payload)
        count = 0
        while log:
            message_json = Rds.redis_conn.brpop("mod_queue" , timeout=3)
            try:
                _,y = message_json
                message = loads(y)
                if message["name"] == username:
                    count = 0
                    process(message)
                else:
                    count = count + 1
                    Rds.redis_conn.lpush("mod_queue" , dumps(message))
                    if count == 50:
                        print("\nDONE\n")
                        break
            except:
                print("\nDone\n")
                break
    else:
        print("\nNe mai auzim")
        exit()

def login():

    for i in range(NO_OF_TRIES):
        global username
        global password
        username = input("Username : ")
        password = input("Password : ")
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
                pprint(result)
            print("\nLogin successfull\n")
            return True
    else:
        return False           

def sign_in():
    for i in range(NO_OF_TRIES):
        username = input("Username : ")
        password = input("Password : ")
        password = hash(password)

        payload = {
            "name" : username,
            "password" : password
        }
        payload = dumps(payload)

        response = requests.post("http://localhost:8000/sign-in" , data=payload)
        if response.status_code == 200:
            print("\n\nSign in successfull, please log in\n\n")
            login()
            break
        if i == NO_OF_TRIES:
            print("\nTry again later\n")
            exit()

choice = int(input("choices :\n  1. Sign-in\n  2. Login\n"))

if choice == 1:
    sign_in()
elif choice == 2:
    log = login()
else:
    print("choice not valid")
    exit()

transaction()