# -*- coding: utf-8 -*-
"""
Esqueleto de otro agente usando los servicios web de Flask

/comm es la entrada para la recepcion de mensajes del agente
/Stop es la entrada que para el agente

Tiene una funcion AgentBehavior2 que se lanza como un thread concurrente

Asume que el agente de registro esta en el puerto 5000

@author: tu_nombre
"""

from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph
from flask import Flask

from utils.FlaskServer import shutdown_server
from utils.Agent import Agent

__author__ = 'tu_nombre'

# Configuration stuff
hostname = socket.gethostname()
port = 9020  # Cambiar al puerto que desees para este agente

agn = Namespace("http://www.agentes.org#")

# Contador de mensajes
mss_cnt = 0

# Datos del Agente

AgenteTemplate2 = Agent('AgentTemplate2',
                        agn.AgentTemplate2,
                        'http://%s:%d/comm' % (hostname, port),
                        'http://%s:%d/Stop' % (hostname, port))

# Directory agent address
DirectoryAgent = 'http://localhost:5000/register'  # Cambiar si el servicio de registro no está en localhost:5000

# Global triplestore graph
dsgraph = Graph()

cola2 = Queue()

# Flask stuff
app = Flask(__name__)


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt
    pass


@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente

    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


def tidyup():
    """
    Acciones previas a parar el agente

    """
    pass


def agentbehavior2(cola):
    """
    Un comportamiento del agente

    :return:
    """
    pass


if __name__ == '__main__':
    # Ponemos en marcha los behaviors
    ab2 = Process(target=agentbehavior2, args=(cola2,))
    ab2.start()

    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    ab2.join()
    print('The End')



from flask import Flask, render_template, request, jsonify
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF

app = Flask(__name__)

# Directory of agents
agents = {
    'Agent1': 'http://localhost:5001',
    'Agent2': 'http://localhost:5002',
    'SellerAgent': 'http://localhost:5003'
}

@app.route('/')
def home():
    return "Directory Service"

@app.route('/agents')
def list_agents():
    return jsonify(agents)

@app.route('/agents/<name>')
def get_agent(name):
    location = agents.get(name)
    if location:
        return jsonify({'name': name, 'location': location})
    else:
        return "Agent not found", 404

@app.route('/register', methods=['POST'])
def register_agent():
    agent_data = request.get_json()
    agents[agent_data['name']] = agent_data['location']
    return jsonify(agents), 201

@app.route('/retorn', methods=['GET', 'POST'])
def retorn():
    archivo_base_datos = "data/compres.rdf"
    base_datos = leer_DB(archivo_base_datos)

    compres = []
    ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
    
    for compra in base_datos.subjects(RDF.type, ns.Compra):
        nomCompra = str(base_datos.value(compra, ns.Nombre))
        preuCompra = str(base_datos.value(compra, ns.PreuTotal))
        items = [str(item) for item in base_datos.objects(compra, ns.TéProducte)]
        compres.append((nomCompra, items, preuCompra))

    count = max(len(item[1]) for item in compres) if compres else 0
    sizes = [len(item[1]) for item in compres]

    if request.method == 'POST':
        selected_items = request.form.getlist('checkbox')
        selected_items = [int(item) for item in selected_items]
        # Aquí puedes procesar los productos seleccionados para devolver
        print("Productos a devolver:", selected_items)
        # Procesar las devoluciones y actualizar la base de datos
        return jsonify({'message': 'Devoluciones procesadas', 'items': selected_items})

    return render_template('retorn.html', compres=compres, count=count, sizes=sizes)

def leer_DB(ruta_archivo):
    # Cargar el grafo RDF desde el archivo
    g = Graph()
    try:
        g.parse(ruta_archivo, format="xml")
        num_tripletas = len(g)
        print(f"Se han cargado {num_tripletas} tripletas desde el archivo RDF.")
    except Exception as e:
        print("Error:", e)
    return g

def mostrar_DB(base_datos):
    # Mostrar todas las tripletas en la base de datos
    for subj, pred, obj in base_datos:
        print(f"Sujeto: {subj}, Predicado: {pred}, Objeto: {obj}")

def añadir_producto(base_datos, nombre_producto):
    ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
    producte_uri = ns.Producte_3333 # Cambiar el URI según corresponda
    base_datos.add((producte_uri, RDF.type, ns.Producte))
    base_datos.add((producte_uri, ns.Nombre, Literal(nombre_producto)))
    
def añadir_compra(base_datos, nomCompra, preuCompra, dataEntrega):
    ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
    compra_uri = ns.Compra_C # Cambiar el URI según corresponda
    base_datos.add((compra_uri, RDF.type, ns.Compra))
    base_datos.add((compra_uri, ns.PreuTotal, Literal(preuCompra)))
    base_datos.add((compra_uri, ns.DataEntrega, Literal(dataEntrega)))

def guardar_DB(base_datos, ruta_archivo):
    # Guardar los valores en el archivo de la base de datos
    base_datos.serialize(destination=ruta_archivo, format="xml")

if __name__ == "__main__":
    app.run(port=5000)
