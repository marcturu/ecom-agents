import os
import signal
import socket
from multiprocessing import Process, Queue
from pathlib import Path

import psutil
import requests
from flask import Flask, jsonify, request
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

from app.utils.ACL import ACL
from app.utils.ACLMessages import build_message, get_message_properties
from app.utils.Agent import Agent
from app.utils.FlaskServer import shutdown_server

# Configuration
hostname = socket.gethostname()
port = 5003  # Use a different port for this agent

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

        if performative == ACL.request:
            if action == ECSDI.DispatchProduct:
                product_name = msg_graph.value(
                    subject=content, predicate=ECSDI.Producte_comprat)
                delivery_address = msg_graph.value(
                    subject=content, predicate=ECSDI.Direccio_entrega)
                delivery_city = msg_graph.value(
                    subject=content, predicate=ECSDI.Ciutat_entrega)

                # Query LogisticCenterAgent instances to find the one with the matching city
                logistic_agents = ['LogisticCenterAgent']  # Example list
                selected_agent = None

                for agent in logistic_agents:
                    agent_url = get_agent_dir(agent)
                    if agent_url:
                        agent_city = query_location(agent_url)
                        if agent_city == str(delivery_city):
                            selected_agent = agent_url
                            break

                if selected_agent:
                    # Send message to the selected LogisticCenterAgent
                    dispatch_graph = Graph()
                    dispatch_graph.add(
                        (URIRef(''), RDF.type, ECSDI.ReceiveProduct))
                    dispatch_graph.add((URIRef(''), ECSDI.Producte_comprat, Literal(
                        product_name, datatype=XSD.string)))
                    dispatch_graph.add((URIRef(''), ECSDI.Direccio_entrega, Literal(
                        delivery_address, datatype=XSD.string)))

                    dispatch_message = build_message(
                        dispatch_graph, ACL.request, sender=agent_uri, receiver=URIRef(selected_agent + '/comm'))
                    requests.post(selected_agent + '/comm', data=dispatch_message.serialize(format='turtle'),
                                  headers={'Content-Type': 'application/x-turtle'})
                else:
                    print(f"No matching LogisticCenterAgent found for city: {
                          delivery_city}")

        return jsonify({"status": "ok"}), 200
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
