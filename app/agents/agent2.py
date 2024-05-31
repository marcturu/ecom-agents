import socket
from multiprocessing import Process, Queue

import requests
from flask import Flask, request
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

from app.utils.Agent import Agent
from app.utils.FlaskServer import shutdown_server

# Configuration stuff
hostname = socket.gethostname()
port = 9030  # Example port, adjust as needed

# Directory agent address
directory_address = 'http://localhost:9000/Register'

# Namespace for the ontology
ECSDI = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

# Global triplestore graph
dsgraph = Graph()

# Agent Definition
AgentTemplate = Agent('AgentTemplate',
                      ECSDI.AgentTemplate,
                      f'http://{hostname}:{port}/comm',
                      f'http://{hostname}:{port}/Stop')

# Flask app
app = Flask(__name__)


@app.route("/Stop")
def stop():
    shutdown_server()
    return "AgentTemplate stopping..."


def agentbehavior(cola):
    while True:
        msg = cola.get()
        if msg == 'STOP':
            break
        print(f"AgentTemplate behavior received message: {msg}")


@app.route("/comm", methods=['POST'])
def communicate():
    global dsgraph
    message = request.get_json()
    print("AgentTemplate received message:", message)

    # Process the received message and create a response if needed
    if message['type'] == 'response':
        print(f"Received product info: {
              message['product']} priced at {message['price']}")
    elif message['type'] == 'request':
        product_info = {
            'type': 'response',
            'product': 'Laptop',
            'price': '1200'
        }
        requests.post('http://localhost:9010/comm', json=product_info)
        print("Response sent from AgentTemplate to Agent1")

    return "OK"


def register_with_directory():
    # Function to register AgentTemplate with the Directory Agent
    registration_info = {
        'name': 'AgentTemplate',
        'address': f'http://{hostname}:{port}/comm'
    }
    requests.post(directory_address, json=registration_info)
    print("AgentTemplate registered with DirectoryAgent")


if __name__ == "__main__":
    # Start the agent behavior as a separate process
    cola = Queue()
    p = Process(target=agentbehavior, args=(cola,))
    p.start()

    # Register with the directory agent
    register_with_directory()

    # Run the Flask app
    app.run(host=hostname, port=port)

    # Join the process after the Flask app stops
    p.join()
