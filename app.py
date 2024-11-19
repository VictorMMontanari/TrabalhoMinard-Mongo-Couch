from flask import Flask, request, jsonify
from couchdb_utils import get_document as get_couch_doc, create_document as create_couch_doc, \
    update_document as update_couch_doc, delete_document as delete_couch_doc, get_all_documents as get_all_couch_docs
from mongodb_utils import get_document as get_mongo_doc, create_document as create_mongo_doc, \
    update_document as update_mongo_doc, delete_document as delete_mongo_doc, get_all_documents as get_all_mongo_docs


app = Flask(__name__)


@app.route("/products", methods=["GET"])
def get_all_products():
    """Obtém todos os documentos de acordo com o banco especificado (CouchDB ou MongoDB)."""
    db = request.args.get("db")
    
    if db == "couchdb":
        data = get_all_couch_docs()
    else:
        data = get_all_mongo_docs()
    
    return jsonify(data), 200 if data else 404

@app.route("/product/<string:doc_id>", methods=["GET"])
def get_product(doc_id):
    """Obtém um produto de acordo com o banco especificado (CouchDB ou MongoDB)."""
    db = request.args.get("db")
    if db == "couchdb":
        data = get_couch_doc(doc_id)
    else:
        data = get_mongo_doc(doc_id)
    return jsonify(data), 200 if data else 404

@app.route("/product", methods=["POST"])
def create_product():
    """Cria um novo produto no banco especificado e sincroniza no outro banco."""
    data = request.json
    db = request.args.get("db")

    if db == "couchdb":
        # Cria o produto no CouchDB e sincroniza no MongoDB
        response = create_couch_doc(data)
        create_mongo_doc(data)  # Sincroniza com MongoDB
    else:
        # Cria o produto no MongoDB e sincroniza no CouchDB
        response = create_mongo_doc(data)
        create_couch_doc(data)  # Sincroniza com CouchDB

    return jsonify({"message": "Produto criado e sincronizado", "data": response}), 201

@app.route("/product/<string:doc_id>", methods=["PUT"])
def update_product(doc_id):
    """Atualiza um produto existente no banco especificado e sincroniza no outro banco."""
    data = request.json  # Obtém os dados enviados no corpo da requisição
    db = request.args.get("db")

    # Verificar se os dados estão no formato correto
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400

    try:
        if db == "couchdb":
            # Atualiza no CouchDB e sincroniza a atualização no MongoDB
            response = update_couch_doc(doc_id, data)
            update_mongo_doc(doc_id, data)  # Sincroniza com MongoDB
        else:
            # Atualiza no MongoDB e sincroniza a atualização no CouchDB
            response = update_mongo_doc(doc_id, data)
            update_couch_doc(doc_id, data)  # Sincroniza com CouchDB

        if response:
            return jsonify({"message": "Produto atualizado e sincronizado", "data": data}), 200
        else:
            return jsonify({"error": "Documento não encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/product/<string:doc_id>", methods=["DELETE"])
def delete_product(doc_id):
    """Remove um produto do banco especificado e sincroniza a remoção no outro banco."""
    db = request.args.get("db")

    if db == "couchdb":
        # Deleta no CouchDB e sincroniza a remoção no MongoDB
        response = delete_couch_doc(doc_id)
        delete_mongo_doc(doc_id)  # Sincroniza com MongoDB
    else:
        # Deleta no MongoDB e sincroniza a remoção no CouchDB
        response = delete_mongo_doc(doc_id)
        delete_couch_doc(doc_id)  # Sincroniza com CouchDB
        
    return jsonify({"message": "Produto deletado e sincronizado", "data": response}), 200

if __name__ == "__main__":
    app.run(debug=True)
