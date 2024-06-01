import os
import signal
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
port = 5001

self_name = 'Agent1'

# Directory agent address
directory_address_hostname = socket.gethostname()
directory_address_port = 5000
directory_address = f'http://{directory_address_hostname}:{
    directory_address_port}'
directory_address_register = f'{directory_address}/Register'

# Namespace for the ontology
ECSDI = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

# Global triplestore graph
dsgraph = Graph()

# Agent Definition
Agent1 = Agent('Agent1', ECSDI.Agent1,
               f'http://{hostname}:{port}/comm', f'http://{hostname}:{port}/Stop')

# Flask app
app = Flask(__name__)


@app.route("/Stop")
def stop():
    try:
        shutdown_server()
    except Exception as e:
        print(f"Error stopping server: {e}")
        print('Using Alternative stopping method...')
        os.kill(os.getpid(), signal.SIGINT)

    return "Agent1 stopping..."


def agentbehavior(cola):
    while True:
        msg = cola.get()
        if msg == 'STOP':
            break
        print(f"Agent1 behavior received message: {msg}")


def get_agent_dir(sender):
    response = requests.get(f'{directory_address}/GetAgents')
    response_body = response.json()
    sender_address = response_body.get(sender)
    return sender_address


@app.route("/comm", methods=['POST'])
def communicate():
    global dsgraph
    message = request.get_json()
    print("Agent1 received message:", message)

    if message['type'] == 'response':
        print(f"Received product info: {
              message['product']} priced at {message['price']}")
    elif message['type'] == 'request':
        if message['performative'] == 'infoProd':
            product = message['product']
            # TODO: fetch product from the directory
            response_body = {
                'type': 'request',
                'product': product,
                'sender': self_name,
                'performative': message['performative']
            }
            url = get_agent_dir('Agent2')
            requests.post(url, json=response_body)
        else:
            print("Invalid performative")

    return "OK"


def register_with_directory():
    registration_info = {
        'name': self_name,
        'address': f'http://{hostname}:{port}/comm'
    }
    requests.post(directory_address_register, json=registration_info)
    print("Agent1 registered with DirectoryAgent")


if __name__ == "__main__":
    cola = Queue()
    p = Process(target=agentbehavior, args=(cola,))
    p.start()

    register_with_directory()

    app.run(host=hostname, port=port)

    p.join()
