from pymongo import MongoClient
import os

class Mongo():
    def __init__(self):
        self.database = "image_enhancer"
        self.connection = self.connect_database()
    
    def connect_database(self):
        connection_string = os.getenv("MONGODB_URL", "mongodb+srv://image_dev:123abc@raiden.ggckb0c.mongodb.net/?retryWrites=true&w=majority&appName=Raiden")
        client = MongoClient(connection_string)
        return client[self.database]
    
    def save_to_mongo(self, payload, collection_name):
        try:
            database = self.connection
            collection = database[collection_name]
            collection.insert_one(payload)
            return True
        except Exception:
            return False
        
    def fetch_from_mongo(self, id, collection_name):
        try:
            database = self.connection
            collection = database[collection_name]

            if collection_name == 'wa_image':
                pipeline = [
                    {
                       '$match':{
                           'image_id':id
                       }
                    }
                    
                ]
            if collection_name == "image_resolution":
                pipeline = [
                    {
                       '$match':{
                           "entry.changes.value.contacts.wa_id":id
                       }
                    }
                    
                ]
                result = list(collection.aggregate(pipeline))[0]['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                res = tuple(map(int,result.split('*')))
                return res
            result = list(collection.aggregate(pipeline))[0]
            return result
        except Exception:
            return None