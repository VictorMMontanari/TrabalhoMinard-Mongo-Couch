import os
import requests
from dotenv import load_dotenv
import json

# Carregar variáveis do arquivo .env
load_dotenv()

# Configurações do CouchDB a partir do .env
COUCHDB_URL = os.getenv("COUCHDB_URL")
COUCHDB_USER = os.getenv("COUCHDB_USER")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD")
COUCHDB_NAME = os.getenv("COUCHDB_NAME")

# Verificação se todas as variáveis foram carregadas corretamente
if not all([COUCHDB_URL, COUCHDB_USER, COUCHDB_PASSWORD, COUCHDB_NAME]):
    raise ValueError("Variáveis de ambiente CouchDB não foram carregadas corretamente.")

# Função genérica para requisições no CouchDB
def couchdb_request(method: str, endpoint: str, data: dict = None):
    url = f"{COUCHDB_URL}/{COUCHDB_NAME}{endpoint}"
    auth = (COUCHDB_USER, COUCHDB_PASSWORD)
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.request(method, url, json=data, auth=auth, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
        return None
    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

# Função para obter um documento pelo ID
def get_document(doc_id: str):
    """Obtém um documento específico pelo ID no CouchDB."""
    return couchdb_request("GET", f"/{doc_id}")

# Função para criar um novo documento
def create_document(data: dict):
    """Cria um novo documento no CouchDB."""
    return couchdb_request("POST", "/", data)

# Função para atualizar um documento existente (inclui _rev)
def update_document(doc_id: str, data: dict):
    """Atualiza um documento específico no CouchDB."""
    existing_doc = get_document(doc_id)
    if not existing_doc:
        print(f"Documento {doc_id} não encontrado.")
        return None

    # Adicionar _rev ao documento para evitar conflitos
    data["_rev"] = existing_doc.get("_rev")
    return couchdb_request("PUT", f"/{doc_id}", data)

# Função para deletar um documento pelo ID (inclui _rev)
def delete_document(doc_id: str):
    """Remove um documento específico do CouchDB."""
    existing_doc = get_document(doc_id)
    if not existing_doc:
        print(f"Documento {doc_id} não encontrado.")
        return None

    # Necessário fornecer o _rev para deletar o documento
    return couchdb_request("DELETE", f"/{doc_id}?rev={existing_doc.get('_rev')}")

# Função para criar o banco de dados se não existir
def create_database():
    url = f"{COUCHDB_URL}/{COUCHDB_NAME}"
    response = requests.put(url, auth=(COUCHDB_USER, COUCHDB_PASSWORD))
    
    if response.status_code == 201:
        print(f"Banco de dados '{COUCHDB_NAME}' criado com sucesso.")
    elif response.status_code == 412:
        print(f"O banco de dados '{COUCHDB_NAME}' já existe.")
    else:
        print(f"Erro ao criar o banco de dados: {response.status_code} - {response.text}")

# Função principal para configurar banco e documentos iniciais
def setup_database_and_document():
    """Configura o banco de dados e carrega documentos iniciais."""
    create_database()
    try:
        with open("estoque_tempo_real.json", "r", encoding="utf-8") as f:
            documentos = json.load(f)
            if isinstance(documentos, list):
                for document in documentos:
                    response = create_document(document)
                    if response:
                        print(f"Documento criado: {response['id']}")
            else:
                print("Formato incorreto: esperado uma lista de documentos.")
    except FileNotFoundError:
        print("Arquivo 'estoque_tempo_real.json' não encontrado.")
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON.")

if __name__ == '__main__':
    setup_database_and_document()
