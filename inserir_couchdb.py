import json
import requests
from dotenv import load_dotenv
import os

# Carregar variáveis do ambiente
load_dotenv()

# Obter as variáveis de ambiente
COUCHDB_URL = os.getenv("COUCHDB_URL")
COUCHDB_USER = os.getenv("COUCHDB_USER")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD")
COUCHDB_NAME = os.getenv("COUCHDB_NAME")

# Validar se as variáveis de ambiente foram carregadas corretamente
if not COUCHDB_URL or not COUCHDB_USER or not COUCHDB_PASSWORD or not COUCHDB_NAME:
    raise ValueError("Certifique-se de que as variáveis COUCHDB_URL, COUCHDB_USER, COUCHDB_PASSWORD e COUCHDB_NAME estão definidas no arquivo .env")

# Configurar URL e autenticação
auth = (COUCHDB_USER, COUCHDB_PASSWORD)
db_url = f"{COUCHDB_URL}{COUCHDB_NAME}"

# Função para verificar se o banco de dados existe, e criar caso não exista
def check_or_create_db():
    response = requests.get(db_url, auth=auth)
    if response.status_code == 404:
        print(f"Banco de dados '{COUCHDB_NAME}' não encontrado. Criando...")
        response = requests.put(db_url, auth=auth)
        if response.status_code == 201:
            print(f"Banco de dados '{COUCHDB_NAME}' criado com sucesso!")
        else:
            print(f"Erro ao criar o banco de dados: {response.status_code}, {response.text}")
            exit(1)
    elif response.status_code != 200:
        print(f"Erro ao conectar ao CouchDB: {response.status_code}, {response.text}")
        exit(1)

# Verificar ou criar banco de dados
check_or_create_db()

try:
    # Ler o arquivo JSON
    with open('estoque_tempo_real.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Inserir os documentos no CouchDB com `id_produto` como `_id`
    if isinstance(data, list):
        # Atualizar cada documento para usar `id_produto` como `_id`
        for doc in data:
            if 'id_produto' in doc:
                doc['_id'] = doc['id_produto']

        # Inserir vários documentos usando _bulk_docs
        bulk_docs = {"docs": data}
        response = requests.post(f"{db_url}/_bulk_docs", auth=auth, json=bulk_docs)
        if response.status_code == 201:
            print(f"{len(data)} documentos importados com sucesso!")
        else:
            print(f"Erro ao inserir documentos: {response.status_code}, {response.text}")
    else:
        # Para um único documento, usar `id_produto` como `_id`
        if 'id_produto' in data:
            data['_id'] = data['id_produto']

        # Inserir um único documento
        response = requests.post(db_url, auth=auth, json=data)
        if response.status_code == 201:
            print("1 documento importado com sucesso!")
        else:
            print(f"Erro ao inserir documento: {response.status_code}, {response.text}")

except FileNotFoundError:
    print("Erro: Arquivo JSON 'estoque_tempo_real.json' não encontrado. Verifique o caminho e o nome do arquivo.")
except json.JSONDecodeError:
    print("Erro: O arquivo não está em um formato JSON válido.")
except requests.RequestException as e:
    print(f"Erro ao conectar ou inserir no CouchDB: {e}")
