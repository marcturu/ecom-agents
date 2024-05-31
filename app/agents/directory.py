from flask import Flask, render_template, jsonify, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF

app = Flask(__name__)

# Directory of agents
agents = {
    'Agent1': 'http://localhost:5001',
    'Agent2': 'http://localhost:5002',
    'SellerAgent': 'http://localhost:5003',
    'AgentExtern': 'http://localhost:5004',
    'AgentValoracions': 'http://localhost:5005'
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
  
    archivo_base_datos = "../data/compres.rdf"
    base_datos = leer_DB(archivo_base_datos)
    
    # Mostrar los productos existentes
    print("Compras existentes en la base de datos:")
    mostrar_DB(base_datos)
    
    # Añadir un nuevo producto
    nomCompra = "Compra Antonia"
    preuCompra = "80"
    dataEntrega = "20/10/2024"
    añadir_compra(base_datos, nomCompra, preuCompra, dataEntrega)
    
    # Guardar los cambios en la base de datos
    guardar_DB(base_datos, archivo_base_datos)


