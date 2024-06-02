import os
import signal
import socket
from multiprocessing import Process, Queue
from pathlib import Path

import psutil
import requests
from flask import Flask, redirect, render_template, request, url_for
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

from app.utils.ACL import ACL
from app.utils.ACLMessages import (build_message, get_message_properties,
                                   send_message)
from app.utils.Agent import Agent
from app.utils.DSO import DSO
from app.utils.FlaskServer import shutdown_server

# Configuration
hostname = socket.gethostname()
port = 5005  # Use a different port for this agent

self_name = 'InterfaceAgent'
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
InterfaceAgent = Agent(self_name, ECSDI.InterfaceAgent,
                       f'http://{hostname}:{port}/comm', f'http://{hostname}:{port}/Stop')

# Flask app
app = Flask(__name__, template_folder='templates')


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
    return "InterfaceAgent stopping..."


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


def create_performative_request(product_name, delivery_address, delivery_city):
    # Create a new RDF graph
    g = Graph()

    # Define the request as an individual
    request = URIRef(
        "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#Request")

    # Add product details to the graph
    g.add((request, RDF.type, ECSDI.DispatchProduct))
    g.add((request, ECSDI.Producte_comprat, Literal(
        product_name, datatype=XSD.string)))
    g.add((request, ECSDI.Direccio_entrega, Literal(
        delivery_address, datatype=XSD.string)))
    g.add((request, ECSDI.Ciutat_entrega, Literal(
        delivery_city, datatype=XSD.string)))
    g.add((request, ECSDI.necessita_trasport, Literal(True, datatype=XSD.boolean)))

    return g


@app.route("/")
def index():
    return render_template('dispatch_product.html')


@app.route("/dispatch", methods=["POST"])
def dispatch_product():
    product_name = request.form['product_name']
    delivery_address = request.form['delivery_address']
    delivery_city = request.form['delivery_city']

    # Create the RDF graph for the request
    dispatch_graph = create_performative_request(
        product_name, delivery_address, delivery_city)

    # Use build_message to construct the ACL message
    sender = agent_uri
    receiver_base_url = get_agent_dir('LogisticCenterAdministratorAgent')
    perf = ACL.request

    if receiver_base_url:
        receiver = f"{receiver_base_url}/comm"
        # Build the message
        dispatch_message = build_message(
            dispatch_graph, perf, sender=sender, receiver=URIRef(receiver))

        # Log the message being sent
        print(f"Sending message to {receiver} with content:\n{
              dispatch_message.serialize(format='turtle')}")

        # Send the message
        response = requests.post(receiver, data=dispatch_message.serialize(format='turtle'),
                                 headers={'Content-Type': 'application/x-turtle'})
        return response.content, response.status_code
    else:
        return "Logistic Center Administrator Agent not found", 404


@app.route("/comm", methods=['POST'])
def communicate():
    global data_storage_graph
    message = request.get_data()

    try:
        # Extract message properties
        msg_graph = Graph()
        msg_graph.parse(data=message, format='turtle')
        msg_props = get_message_properties(msg_graph)

        performative = msg_props['performative']
        sender = msg_props['sender']
        receiver = msg_props['receiver']
        content = msg_props['content']
        action = None
        for s, p, o in msg_graph.triples((content, RDF.type, None)):
            if o.startswith(ECSDI):
                action = o
                break

        # Log the received action and content
        print(f"Received message with action: {action}")
        print(f"Content: {content}")

        # Handle different performatives
        if performative == ACL.inform:
            pass
        elif performative == ACL.request:
            if action == ECSDI.QueryProductAvailability:
                product_id = msg_graph.value(
                    subject=content, predicate=ECSDI.productID)
                # Query the logistic center for product availability
                logistic_center_address = get_agent_dir(
                    'LogisticCenterAdministratorAgent')
                if logistic_center_address:
                    query_graph = Graph()
                    query_graph.add(
                        (URIRef(''), RDF.type, ECSDI.QueryProductAvailability))
                    query_graph.add(
                        (URIRef(''), ECSDI.productID, Literal(product_id)))
                    query_message = build_message(
                        query_graph, ACL['query-if'], agent_uri, URIRef(logistic_center_address))
                    response = requests.post(
                        logistic_center_address + '/comm', data=query_message.serialize(format='turtle'))
                    return response.content, response.status_code
            elif action == ECSDI.InsertProduct:
                # Register a new product in the lots agent
                lots_address = get_agent_dir('LotAdministratorAgent')
                if lots_address:
                    insert_graph = Graph()
                    product = URIRef(
                        f"http://example.org/product/{msg_graph.value(subject=content, predicate=ECSDI.productID)}")
                    insert_graph.add((product, RDF.type, ECSDI.Product))
                    insert_graph.add((product, ECSDI.productID, msg_graph.value(
                        subject=content, predicate=ECSDI.productID)))
                    insert_graph.add((product, ECSDI.productName, msg_graph.value(
                        subject=content, predicate=ECSDI.productName)))
                    insert_graph.add((product, ECSDI.productPrice, msg_graph.value(
                        subject=content, predicate=ECSDI.productPrice)))
                    insert_message = build_message(
                        insert_graph, ACL.request, agent_uri, URIRef(lots_address))
                    response = requests.post(
                        lots_address + '/comm', data=insert_message.serialize(format='turtle'))
                    return response.content, response.status_code
            elif action == ECSDI.DispatchProduct:
                # Dispatch a product
                logistic_center_address = get_agent_dir(
                    'LogisticCenterAdministratorAgent')
                if logistic_center_address:
                    dispatch_graph = create_performative_request(
                        msg_graph.value(subject=content,
                                        predicate=ECSDI.Producte_comprat),
                        msg_graph.value(subject=content,
                                        predicate=ECSDI.Direccio_entrega),
                        msg_graph.value(subject=content,
                                        predicate=ECSDI.Ciutat_entrega)
                    )
                    dispatch_message = build_message(
                        dispatch_graph, ACL.request, agent_uri, URIRef(logistic_center_address))
                    response = requests.post(
                        logistic_center_address + '/comm', data=dispatch_message.serialize(format='turtle'))
                    return response.content, response.status_code
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
        return response_graph.serialize(format='turtle')
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
