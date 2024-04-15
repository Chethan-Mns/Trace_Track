import os
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv()

ca = certifi.where()

client = pymongo.MongoClient(os.environ.get('mongoDB_string')
                             , tlsCAFile=ca)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client [ 'vehispot' ]
