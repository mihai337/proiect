from database import Database

# Database.coll.update_one({"name" : "Mihai"} , {"$set" : {"balance" : 420}})

# Database.coll.delete_one({"name" : "Mihai"})
# Database.coll.delete_one({"name" : "Dora"})
# Database.coll.delete_one({"name" : "Mage"})
Database.coll.delete_one({"name" : "Admin"})
#just a comment
