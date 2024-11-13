from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Carregar variáveis do ambiente
load_dotenv()

# Obter as variáveis de ambiente
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Verificar se as variáveis de ambiente foram carregadas corretamente
if not MONGODB_URI or not DB_NAME or not COLLECTION_NAME:
    raise ValueError("Variáveis de ambiente não configuradas corretamente.")

# Conexão com o MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    print("Conexão com o MongoDB estabelecida com sucesso.")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    raise

def get_collection():
    """Obtém a coleção de estoque."""
    return db[COLLECTION_NAME]

def get_document(doc_id: str):
    """Obtém um documento pelo campo 'id_produto'."""
    collection = get_collection()
    document = collection.find_one({"id_produto": doc_id}, {"_id": 0})
    return document if document else {"message": "Documento não encontrado"}

def create_document(data: dict):
    """Cria um novo documento no MongoDB."""
    collection = get_collection()
    try:
        result = collection.insert_one(data)
        return result.inserted_id
    except Exception as e:
        print(f"Erro ao criar documento: {e}")
        return None

def update_document(doc_id: str, data: dict):
    """Atualiza um documento existente no MongoDB."""
    collection = get_collection()
    result = collection.update_one({"id_produto": doc_id}, {"$set": data})
    return result.modified_count > 0


def delete_document(doc_id: str):
    """Remove um documento do MongoDB."""
    collection = get_collection()
    try:
        result = collection.delete_one({"produto_id": doc_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Erro ao deletar documento: {e}")
        return False
