from database import Database

Database.coll.update_one({"name" : "Mihai"} , {"$set" : {"balance" : 420}})

#just a comment
