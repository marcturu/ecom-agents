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
port = 5003

self_name = 'LogisticCenterAdministratorAgent'
agent_uri = URIRef(f'http://{hostname}:{port}/{self_name}')
data_folder = Path('app/data')
data_file_path = data_folder / f'{self_name}_data.ttl'

# Ensure the data folder exists
data_folder.mkdir(parents=True, exist_ok=True)

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
LogisticCenterAdministratorAgent = Agent(self_name, ECSDI.LogisticCenterAdministratorAgent,
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
        return str(e), 500


def agentbehavior(queue):
    while True:
        msg = queue.get()
        if msg == 'STOP':
            break


def get_agent_dir(sender):
    try:
        response = requests.get(f'{directory_address}/GetAgents')
        response_body = response.json()
        sender_address = response_body.get(sender)
        return sender_address
    except Exception:
        return None


@app.route("/comm", methods=['POST'])
def communicate():
    global data_storage_graph
    message = request.data.decode('utf-8')

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

        # Handle different performatives
        if performative == ACL.inform:
            pass
        elif performative == ACL.request:
            if action == ECSDI.DispatchProduct:
                product_name = msg_graph.value(
                    subject=content, predicate=ECSDI.Producte_comprat)
                delivery_address = msg_graph.value(
                    subject=content, predicate=ECSDI.Direccio_entrega)
                delivery_city = msg_graph.value(
                    subject=content, predicate=ECSDI.Ciutat_entrega)
                # Implement your logic to handle the product dispatch here
                # For example, log the dispatch details
                print(f"Dispatching product: {product_name}")
                print(f"Delivery address: {delivery_address}")
                print(f"Delivery city: {delivery_city}")
            elif action == ECSDI.DeleteProduct:
                delete_query = f"""
                DELETE WHERE {{
                    ?product a <{ECSDI.Product}> ;
                             <{ECSDI.productID}> "{content}" .
                }}
                """
                sparql_wrapper = SPARQLWrapper(sparql_endpoint)
                sparql_wrapper.setQuery(delete_query)
                sparql_wrapper.setMethod(POST)
                sparql_wrapper.query()
        elif performative == ACL.confirm:
            pass
        elif performative == ACL['query-if']:
            pass
        elif performative == ACL['query-ref']:
            pass
        elif performative == ACL.disconfirm:
            pass
        elif performative == ACL.subscribe:
            pass
        elif performative == ACL.propose:
            pass
        elif performative == ACL.cancel:
            pass
        else:
            return "Unknown performative", 400

        # Build and send response message
        response_graph = Graph()
        response_graph = build_message(
            response_graph, performative, agent_uri, sender, content)
        return response_graph.serialize(format='turtle'), 200
    except Exception as e:
        return str(e), 500


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
