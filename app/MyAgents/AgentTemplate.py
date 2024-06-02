import logging
import os
import signal
import socket
from multiprocessing import Process, Queue

import psutil
import requests
from flask import Flask, jsonify, request
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF
from SPARQLWrapper import DELETE, INSERT, JSON, POST, SELECT, SPARQLWrapper

from app.utils.ACL import (CANCEL, CONFIRM, DISCONFIRM, INFORM, PROPOSE,
                           QUERY_IF, QUERY_REF, REQUEST, SUBSCRIBE)
from app.utils.ACLMessages import (build_message, get_message_properties,
                                   send_message)
from app.utils.Agent import Agent
from app.utils.DSO import DSO
from app.utils.FlaskServer import shutdown_server

# Configuration
hostname = socket.gethostname()
port = 5002

self_name = 'NewAgent'
agent_uri = URIRef(f'http://{hostname}:{port}/{self_name}')
data_folder = 'app/data'
data_file_path = os.path.join(data_folder, f'{self_name}_data.ttl')

# Ensure the data folder exists
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Directory agent address
directory_address_hostname = socket.gethostname()
directory_address_port = 5000
directory_address = f'http://{
    directory_address_hostname}:{directory_address_port}'
directory_address_register = f'{directory_address}/Register'

# Namespace for the ontology
ECSDI = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
DSO = Namespace(
    "http://www.semanticweb.org/ontologies/2024/4/DirectoryService#")

# Global triplestore graph
data_storage_graph = Graph()

# Load ontology data
ontology_path = 'app/ontologiaTTL/Ontologies_v8.ttl'
data_storage_graph.parse(ontology_path, format='turtle')

# Load stored data if exists
if os.path.exists(data_file_path):
    data_storage_graph.parse(data_file_path, format='turtle')

# Agent Definition
NewAgent = Agent(self_name, ECSDI.NewAgent,
                 f'http://{hostname}:{port}/comm', f'http://{hostname}:{port}/Stop')

# Flask app
app = Flask(__name__)

# SPARQL Endpoint
sparql_endpoint = f'http://{hostname}:{port}/sparql'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_data():
    try:
        with open(data_file_path, 'w') as f:
            f.write(data_storage_graph.serialize(format='turtle'))
        logger.info("Data successfully saved.")
    except Exception as e:
        logger.error(f"Error saving data: {e}")


@app.route("/Stop")
def stop():
    try:
        save_data()
        shutdown_server()
    except Exception as e:
        logger.error(f"Error stopping server: {e}")
        print('Using Alternative stopping method...')
        kill_child_processes(os.getpid())
        os.kill(os.getpid(), signal.SIGINT)

    return "NewAgent stopping..."


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


@app.route("/sparql", methods=['POST'])
def sparql():
    query = request.form.get('query', '')
    sparql_wrapper = SPARQLWrapper(sparql_endpoint)
    sparql_wrapper.setQuery(query)
    sparql_wrapper.setReturnFormat(JSON)

    try:
        if query.strip().upper().startswith('SELECT'):
            sparql_wrapper.setMethod(POST)
            sparql_wrapper.setQueryType(SELECT)
        elif query.strip().upper().startswith('CONSTRUCT'):
            sparql_wrapper.setReturnFormat(RDF)
            results = sparql_wrapper.query().convert()
            return results.serialize(format='turtle')
        elif query.strip().upper().startswith('DELETE'):
            sparql_wrapper.setMethod(POST)
            sparql_wrapper.setQueryType(DELETE)
            results = sparql_wrapper.query().convert()
            return jsonify(results)
        else:
            sparql_wrapper.setQueryType(INSERT)
            results = sparql_wrapper.query().convert()
            return jsonify(results)
    except Exception as e:
        logger.error(f"Error processing SPARQL query: {e}")
        return str(e), 500


def agentbehavior(queue):
    while True:
        msg = queue.get()
        if msg == 'STOP':
            break
        logger.info(f"NewAgent behavior received message: {msg}")


def get_agent_dir(sender):
    try:
        response = requests.get(f'{directory_address}/GetAgents')
        response_body = response.json()
        sender_address = response_body.get(sender)
        return sender_address
    except Exception as e:
        logger.error(f"Error getting agent directory: {e}")
        return None


@app.route("/comm", methods=['POST'])
def communicate():

    global data_storage_graph
    message = request.get_json()
    logger.info("NewAgent received message")

    try:
        # Extract message properties
        msg_graph = Graph()
        msg_graph.parse(data=message['content'], format='turtle')
        msg_props = get_message_properties(msg_graph)

        performative = msg_props.get('performative')
        sender = msg_props.get('sender')
        receiver = msg_props.get('receiver')
        content = msg_props.get('content')
        action = msg_props.get('action')

        # Handle different performatives
        if performative == INFORM:
            # Handle INFORM performative
            pass
        elif performative == REQUEST:
            if action == DSO.Register:
                # Handle registration logic
                pass
            elif action == DSO.Search:
                # Handle search logic
                pass
            elif action == ECSDI.DeleteProduct:
                # Handle delete product logic
                pass
        elif performative == CONFIRM:
            # Handle CONFIRM performative
            pass
        elif performative == QUERY_IF:
            # Handle QUERY_IF performative
            pass
        elif performative == QUERY_REF:
            # Handle QUERY_REF performative
            pass
        elif performative == DISCONFIRM:
            # Handle DISCONFIRM performative
            pass
        elif performative == SUBSCRIBE:
            # Handle SUBSCRIBE performative
            pass
        elif performative == PROPOSE:
            # Handle PROPOSE performative
            pass
        elif performative == CANCEL:
            # Handle CANCEL performative
            pass
        else:
            return "Unknown performative", 400

        # Build and send response message
        response_graph = Graph()
        response_graph = build_message(
            response_graph, performative, agent_uri, sender, content)

        return response_graph.serialize(format='turtle')
    except Exception as e:
        logger.error(f"Error processing communication: {e}")
        return str(e), 500


def register_with_directory():
    try:
        registration_info = {
            'name': self_name,
            'address': f'http://{hostname}:{port}/comm'
        }
        requests.post(directory_address_register, json=registration_info)
        logger.info("NewAgent registered with DirectoryAgent")
    except Exception as e:
        logger.error(f"Error registering with directory: {e}")


if __name__ == "__main__":
    queue = Queue()
    p = Process(target=agentbehavior, args=(queue,))
    p.start()

    register_with_directory()

    app.run(host=hostname, port=port)

    p.join()
