from database import Database

Database.coll.update_one({"name" : "Mihai"} , {"$set" : {"balance" : 420}})