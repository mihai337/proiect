from msg_broker import Rds
from database import Database
from json import loads,dumps

log = False

def process(message):
    results = Database.coll.find({"name" : message["name"]})
    for result in results:
        balance = result["balance"]
        print(result)
    
        balance = balance + message["value"]
        Database.coll.update_one({"name" : message["name"]} , {"$set" : {"balance" : balance}})
        return {"Update" : "Successful"}
    return {"Error" : "Not found"}

def login():
    global username
    global password

    username = input("Username : ")
    password = input("Password : ")
    results = Database.coll.find({"name" : username})
    for result in results:
        if result["password"] == password:
            return True
        print("Worng password, try again\n")
        return False
    print("Username not found, try again\n")
    return False


for i in range(5):
    log = login()
    if log == True:
        break
else:
    print("Too many tries")

while log:
    message_json = Rds.redis_conn.brpop("mod_queue")
    x,y = message_json
    message = loads(y)
    if message["name"] == username:
        process(message)
    else:
        Rds.redis_conn.lpush("mod_queue" , dumps(message))