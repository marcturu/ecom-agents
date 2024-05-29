from flask import Flask, jsonify, request
from rdflib import Graph, Namespace, RDF, Literal, URIRef
import requests

app = Flask(__name__)

# RDF Graph
graph = Graph()

# Namespaces
#ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

@app.route('/')
def home():
    return "Hello from Seller Agent"


@app.route('/search', methods=['POST'])
def search_products():
    data = request.get_json()
    # Aquí puedes procesar la búsqueda en tu RDF graph
    # Por ejemplo, puedes usar una consulta SPARQL en el graph para buscar productos

    return jsonify({'products': []})


@app.route('/send_message_to_agent1', methods=['POST'])
def send_message_to_agent1():
    # Crear un mensaje RDF
    graph = Graph()
    # Crear un sujeto, predicado y objeto para el mensaje
    subject = URIRef("http://example.org/message")
    predicate = URIRef("http://example.org/hasContent")
    obj = Literal("Hello from Seller Agent to Agent 1")

    # Agregar la tripleta al grafo
    graph.add((subject, predicate, obj))

    # Serializar el mensaje a RDF/XML
    serialized_message = graph.serialize(format='xml')

    # Enviar el mensaje al agente 1
    url_agent1 = 'http://localhost:5001/receive_message'
    headers = {'Content-Type': 'application/rdf+xml'}
    response = requests.post(url_agent1, data=serialized_message, headers=headers)

    if response.status_code == 200:
        return "Message sent to Agent 1 successfully"
    else:
        return "Failed to send message to Agent 1"
    

def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'SellerAgent',
        'location': 'http://localhost:5003'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5003)