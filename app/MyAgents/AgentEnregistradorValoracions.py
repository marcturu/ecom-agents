import os
import signal
import socket
from multiprocessing import Process, Queue
from pathlib import Path

import psutil
import requests
from flask import Flask, jsonify, request
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF
from SPARQLWrapper import DELETE, INSERT, JSON, POST, SELECT, SPARQLWrapper

from app.utils.ACL import ACL
from app.utils.ACLMessages import build_message, get_message_properties
from app.utils.Agent import Agent
from app.utils.DSO import DSO
from app.utils.FlaskServer import shutdown_server

# Configuration
hostname = socket.gethostname()
port = 5008

self_name = 'AgentEnregistradorValoracions'
agent_uri = URIRef(f'http://{hostname}:{port}/{self_name}')
data_folder = Path('app/data')
data_file_path = data_folder / f'{self_name}_data.ttl'

# Ensure the data folder exists
data_folder.mkdir(parents=True, exist_ok=True)

# Directory agent address
directory_address_hostname = socket.gethostname()
directory_address_port = 5000
directory_address = f'http://{directory_address_hostname}:{directory_address_port}'
directory_address_register = f'{directory_address}/Register'

# Namespace for the ontology
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
DSO = Namespace("http://www.semanticweb.org/ontologies/2024/4/DirectoryService#")

# Global triplestore graph
data_storage_graph = Graph()

# Load ontology data
ontology_path = Path('app/ontologiaTTL/Ontologies_v8.ttl').resolve()
ontology_uri = ontology_path.as_uri()
data_storage_graph.parse(ontology_uri, format='turtle')

# Load stored data if exists
data_file_path = data_file_path.resolve()
if data_file_path.exists():
    try:
        data_file_uri = data_file_path.as_uri()
        data_storage_graph.parse(data_file_uri, format='turtle')
    except UnicodeDecodeError:
        pass

# Agent Definition
AgentEnregistradorValoracions = Agent(self_name, ECSDI.AgentEnregistradorValoracions,
                                      f'http://{hostname}:{port}/comm', f'http://{hostname}:{port}/Stop')

# Flask app
app = Flask(__name__)

# SPARQL Endpoint
sparql_endpoint = f'http://{hostname}:{port}/sparql'


def save_data():
    try:
        with open(data_file_path, 'w', encoding='utf-8') as f:
            f.write(data_storage_graph.serialize(format='turtle'))
    except Exception:
        pass


@app.route("/Stop")
def stop():
    try:
        save_data()
        shutdown_server()
    except Exception:
        print('Using Alternative stopping method...')
        kill_child_processes(os.getpid())
        os.kill(os.getpid(), signal.SIGINT)
    return "LogisticCenterAdministratorAgent stopping..."


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        try:
            process.send_signal(sig)
        except psutil.NoSuchProcess:
            continue


def agentbehavior(queue):
    while True:
        msg = queue.get()
        if msg == 'STOP':
            break


def get_agent_dir(agent_name):
    try:
        response = requests.get(f'{directory_address}/GetAgents')
        response_body = response.json()
        agent_address = response_body.get(agent_name)
        if agent_address:
            return agent_address.split('/comm')[0]
        else:
            return None
    except Exception:
        return None


def query_location(agent_url):
    query_graph = Graph()
    query_graph.add((URIRef(''), RDF.type, ECSDI.QueryLocation))

    query_message = build_message(
        query_graph, ACL.request, sender=agent_uri, receiver=URIRef(agent_url))
    response = requests.post(f"{agent_url}/comm", data=query_message.serialize(format='turtle'),
                             headers={'Content-Type': 'application/x-turtle'})
    response_graph = Graph()
    response_graph.parse(data=response.text, format='turtle')

    for _, _, city in response_graph.triples((None, ECSDI.LocationCity, None)):
        return str(city)
    return None


@app.route("/comm", methods=['POST'])
def communicate():
    global data_storage_graph

    message = request.args['content']

    try:
        # Extract message properties
        msg_graph = Graph()
        msg_graph.parse(data=message, format='turtle')
        msg_props = get_message_properties(msg_graph)

        performative = msg_props.get('performative')
        sender = msg_props.get('sender')
        receiver = msg_props.get('receiver')
        content = msg_props.get('content')

        # Extract action from the RDF graph
        action = None
        for s, p, o in msg_graph.triples((None, RDF.type, None)):
            if o.startswith(ECSDI):
                action = o
                content = s
                break

        # Log the extracted values
        print(f"Received message with action: {action}")
        print(f"Content: {content}")

        if performative != ACL.request:
            # If not a request, respond that we didn't understand the message
            resultadoComunicacion = build_message(Graph(), ACL['not-understood'],
                                                  sender=AgentEnregistradorValoracions.uri, receiver=sender, msgcnt=0)
        elif performative == ACL.request:
            # Add product rating
            if action == ECSDI.ValoracioProduct:
                product_name = msg_graph.value(subject=content, predicate=ECSDI.Producte_a_valorar)
                dies_que_sha_entregat = msg_graph.value(subject=content, predicate=ECSDI.dies_que_sha_entregat)
                usuari = msg_graph.value(subject=content, predicate=ECSDI.Usuari)
                valoracio = msg_graph.value(subject=content, predicate=ECSDI.valoracio)
                descripcio = msg_graph.value(subject=content, predicate=ECSDI.descripcio)

                if dies_que_sha_entregat is not None:
                    dies_que_sha_entregat = int(dies_que_sha_entregat)
                    if dies_que_sha_entregat > 5:
                        # Create new graph to store rating information
                        valoracio_graph = Graph()
                        valoracio_uri = URIRef(f"http://www.semanticweb.org/valoracions/{content.split('/')[-1]}")

                        valoracio_graph.add((valoracio_uri, RDF.type, ECSDI.ValoracioProduct))
                        valoracio_graph.add((valoracio_uri, ECSDI.Producte_a_valorar, product_name))
                        valoracio_graph.add((valoracio_uri, ECSDI.dies_que_sha_entregat, Literal(dies_que_sha_entregat)))
                        valoracio_graph.add((valoracio_uri, ECSDI.Usuari, usuari))
                        valoracio_graph.add((valoracio_uri, ECSDI.valoracio, valoracio))
                        valoracio_graph.add((valoracio_uri, ECSDI.descripcio, descripcio))

                        # Save rating to data storage
                        valoracions_file_path = Path('../data/valoracions').resolve()
                        if valoracions_file_path.exists():
                            valoracions_graph = Graph()
                            valoracions_graph.parse(valoracions_file_path.as_uri(), format='turtle')
                            valoracions_graph += valoracio_graph
                        else:
                            valoracions_graph = valoracio_graph

                        valoracions_graph.serialize(destination=valoracions_file_path, format='turtle')

                        resultadoComunicacion = build_message(Graph(), ACL['inform-done'],
                                                              sender=AgentEnregistradorValoracions.uri, receiver=sender, msgcnt=0)
                    else:
                        print("No pots valorar")
                        resultadoComunicacion = build_message(Graph(), ACL['refuse'],
                                                              sender=AgentEnregistradorValoracions.uri, receiver=sender, msgcnt=0)
                else:
                    print("dies_que_sha_entregat no está definido o no tiene valor")
                    resultadoComunicacion = build_message(Graph(), ACL['refuse'],
                                                          sender=AgentEnregistradorValoracions.uri, receiver=sender, msgcnt=0)

        return resultadoComunicacion.serialize(format='xml'), 200

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': 'Bad request'}), 400


def register_with_directory():
    try:
        registration_info = {
            'name': self_name,
            'address': f'http://{hostname}:{port}/comm'
        }
        requests.post(directory_address_register, json=registration_info)
    except Exception:
        pass


if __name__ == "__main__":
    queue = Queue()
    p = Process(target=agentbehavior, args=(queue,))
    p.start()

    register_with_directory()

    try:
        app.run(host=hostname, port=port)
    finally:
        p.terminate()
        p.join()
