import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pymongo.errors import BulkWriteError, PyMongoError

# Carregar variáveis do ambiente
load_dotenv()

# Obter as variáveis de ambiente
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Validar se as variáveis de ambiente foram carregadas corretamente
if not MONGODB_URI or not DB_NAME or not COLLECTION_NAME:
    raise ValueError("Certifique-se de que as variáveis MONGODB_URI, MONGODB_DB e COLLECTION_NAME estão definidas no arquivo .env")

try:
    # Conectar ao MongoDB Atlas
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Ler o arquivo JSON
    with open('estoque_tempo_real.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Inserir os documentos no MongoDB
    if isinstance(data, list):
        try:
            collection.insert_many(data, ordered=False)  # 'ordered=False' para continuar em caso de erro
            print(f"{len(data)} documentos importados com sucesso!")
        except BulkWriteError as bwe:
            print(f"Erro ao inserir documentos: {bwe.details}")
    else:
        collection.insert_one(data)
        print("1 documento importado com sucesso!")

except FileNotFoundError:
    print("Erro: Arquivo JSON não encontrado. Verifique o caminho e o nome do arquivo.")
except json.JSONDecodeError:
    print("Erro: O arquivo não está em um formato JSON válido.")
except PyMongoError as e:
    print(f"Erro ao conectar ou inserir no MongoDB: {e}")
finally:
    # Fechar a conexão
    client.close()
