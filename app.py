from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import gridfs
import io

app = Flask(__name__)
CORS(app)  # Habilita o CORS para todas as rotas

# Configurações do MongoDB
client = MongoClient("mongodb+srv://rodrigosrj:E38gsdWFxh18bBsT@cluster0.twhtu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["meu_banco_de_dados"]
collection = db["minha_colecao"]
fs = gridfs.GridFS(db)

# Função para salvar mídia no GridFS
def salvar_midia(midia):
    if midia:
        file_id = fs.put(midia.read(), filename=midia.filename)
        return str(file_id)
    return None

@app.route('/',)
def index():
        return "Hello, World!"

# Criar um novo documento (Create)
@app.route('/create', methods=['POST'])
def criar_item():
    data = request.form.to_dict()
    midia = request.files.get('midia')

    # Tratar mídia e salvar no GridFS
    midia_id = salvar_midia(midia)
    if midia_id:
        data['midia'] = midia_id

    # Converter campos booleanos
    data['identificar'] = data.get('identificar') == 'true'
    data['resposta'] = data.get('resposta') == 'true'
    data['publicar'] = data.get('publicar') == 'true'

    # Inserir no MongoDB
    resultado = collection.insert_one(data)
    return jsonify({"message": "Item criado com sucesso", "id": str(resultado.inserted_id)}), 201

# Ler todos os documentos (Read)
@app.route('/read', methods=['GET'])
def listar_itens():
    itens = []
    for item in collection.find():
        item['_id'] = str(item['_id'])
        itens.append(item)
    return jsonify(itens), 200

# Ler um documento por ID (sem retornar a mídia)
@app.route('/readone/<item_id>', methods=['GET'])
def ler_item(item_id):
    item = collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        return jsonify({"error": "Item não encontrado"}), 404

    item['_id'] = str(item['_id'])

    return jsonify(item), 200

# Atualizar um documento (Update)
@app.route('/update/<item_id>', methods=['PUT'])
def atualizar_item(item_id):
    data = request.form.to_dict()
    midia = request.files.get('midia')

    # Atualizar a mídia, se for fornecida
    if midia:
        midia_id = salvar_midia(midia)
        data['midia'] = midia_id

    # Converter campos booleanos
    data['identificar'] = data.get('identificar') == 'true'
    data['resposta'] = data.get('resposta') == 'true'
    data['publicar'] = data.get('publicar') == 'true'

    # Atualizar no MongoDB
    resultado = collection.update_one({"_id": ObjectId(item_id)}, {"$set": data})

    if resultado.matched_count == 0:
        return jsonify({"error": "Item não encontrado"}), 404

    return jsonify({"message": "Item atualizado com sucesso"}), 200

# Deletar um documento (Delete)
@app.route('/delete/<item_id>', methods=['DELETE'])
def deletar_item(item_id):
    resultado = collection.delete_one({"_id": ObjectId(item_id)})

    if resultado.deleted_count == 0:
        return jsonify({"error": "Item não encontrado"}), 404

    return jsonify({"message": "Item deletado com sucesso"}), 200


if __name__ == '__main__':
    app.run(debug=False)