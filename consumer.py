from msg_broker import Rds
from database import Database
from json import loads

def process(message):
    results = Database.coll.find({"name" : message["name"]})
    for result in results:
        balance = result["balance"]
        print(result)
    
    balance = balance + message["value"]
    Database.coll.update_one({"name" : message["name"]} , {"$set" : {"balance" : balance}})

while True:
    message_json = Rds.redis_conn.brpop("mod_queue")
    x,y = message_json
    message = loads(y)
    process(message)