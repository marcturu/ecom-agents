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
port = 5004  # Use a different port for this agent

self_name = 'LogisticCenterAgent'
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
LogisticCenterAgent = Agent(self_name, ECSDI.LogisticCenterAgent,
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
    return "LogisticCenterAgent stopping..."


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
        for s, p, o in msg_graph.triples((content, RDF.type, None)):
            if o.startswith(ECSDI):
                action = o
                break

        # Log the extracted values
        print(f"Received message with action: {action}")
        print(f"Content: {content}")

        if performative == ACL.request:
            if action == ECSDI.QueryLocation:
                # Respond with the city location
                response_graph = Graph()
                response_graph.add(
                    (agent_uri, RDF.type, ECSDI.LogisticCenterAgent))
                response_graph.add(
                    (agent_uri, ECSDI.LocationCity, Literal("Mataró", datatype=XSD.string)))

                response_message = build_message(
                    response_graph, ACL.inform, sender=agent_uri, receiver=sender, content=agent_uri)
                return response_message.serialize(format='turtle'), 200

            elif action == ECSDI.ReceiveProduct:
                product_name = msg_graph.value(
                    subject=content, predicate=ECSDI.Producte_comprat)
                delivery_address = msg_graph.value(
                    subject=content, predicate=ECSDI.Direccio_entrega)

                # Update stock quantity and store product information
                product_uri = None
                for s in data_storage_graph.subjects(predicate=ECSDI.Producte_nom, object=Literal(product_name)):
                    product_uri = s
                    stock_quantity = int(data_storage_graph.value(
                        subject=product_uri, predicate=ECSDI.Quantitat_stock))
                    stock_quantity -= 1
                    data_storage_graph.set((product_uri, ECSDI.Quantitat_stock, Literal(
                        stock_quantity, datatype=XSD.integer)))
                    break

                # Store the product and delivery address
                data_storage_graph.add(
                    (URIRef(f'http://example.org/delivery/{product_name}'), RDF.type, ECSDI.ProductDelivery))
                data_storage_graph.add(
                    (URIRef(f'http://example.org/delivery/{product_name}'), ECSDI.Producte_comprat, Literal(product_name, datatype=XSD.string)))
                data_storage_graph.add(
                    (URIRef(f'http://example.org/delivery/{product_name}'), ECSDI.Direccio_entrega, Literal(delivery_address, datatype=XSD.string)))

                save_data()
                print(f"Received product: {product_name}")
                print(f"Delivery address: {delivery_address}")

            elif action == ECSDI.RegisterProduct:
                product_name = msg_graph.value(
                    subject=content, predicate=ECSDI.Producte_nom)
                product_price = msg_graph.value(
                    subject=content, predicate=ECSDI.Producte_preu)
                stock_quantity = msg_graph.value(
                    subject=content, predicate=ECSDI.Quantitat_stock)

                # Store product details in the graph
                product_uri = URIRef(
                    f'http://example.org/product/{product_name}')
                data_storage_graph.add((product_uri, RDF.type, ECSDI.Product))
                data_storage_graph.add(
                    (product_uri, ECSDI.Producte_nom, Literal(product_name, datatype=XSD.string)))
                data_storage_graph.add(
                    (product_uri, ECSDI.Producte_preu, Literal(product_price, datatype=XSD.float)))
                data_storage_graph.add((product_uri, ECSDI.Quantitat_stock, Literal(
                    stock_quantity, datatype=XSD.integer)))

                save_data()
                print(f"Registered product: {product_name}, Price: {
                      product_price}, Stock: {stock_quantity}")

            elif action == ECSDI.QueryProductAvailability:
                product_name = msg_graph.value(
                    subject=content, predicate=ECSDI.Producte_nom)
                if product_name is None:
                    return jsonify({"status": "error", "message": "Product Name not provided"}), 400

                available_stock = 0
                for s in data_storage_graph.subjects(predicate=ECSDI.Producte_nom, object=Literal(product_name)):
                    available_stock = int(data_storage_graph.value(
                        subject=s, predicate=ECSDI.Quantitat_stock))
                    break

                response_graph = Graph()
                response_graph.add(
                    (agent_uri, RDF.type, ECSDI.LogisticCenterAgent))
                response_graph.add(
                    (agent_uri, ECSDI.Producte_nom, Literal(product_name, datatype=XSD.string)))
                response_graph.add((agent_uri, ECSDI.Quantitat_stock, Literal(
                    available_stock, datatype=XSD.integer)))

                response_message = build_message(
                    response_graph, ACL.inform, sender=agent_uri, receiver=sender, content=agent_uri)
                return response_message.serialize(format='turtle'), 200

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
