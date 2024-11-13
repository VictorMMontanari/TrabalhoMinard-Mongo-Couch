import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtenha a senha de uma variável de ambiente
MONGODB_URI = os.getenv("MONGODB_URI")
uri=MONGODB_URI

client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
