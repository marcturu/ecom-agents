from flask import Flask, request, jsonify, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import requests
import uuid

app = Flask(__name__)

CLIENT_URL = "http://localhost:5007" 

# Ruta a la base de datos de compras
archivo_compras = "../data/compres.rdf"
archivo_valoraciones = "../data/valoracions.rdf"

# Definir el namespace
ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

@app.route('/')
def home():
    return """
        <h1>Bienvenido al agente valoraciones</h1>
        <form action="/avisarClient" method="post">
            <input type="submit" value="Iniciar Valoración">
        </form>
        """
    
@app.route('/avisarClient', methods=['POST'])
def avisarClient():
    try:
        response = requests.post(CLIENT_URL + '/TocaValorar')
        if response.status_code == 200:
            return "El cliente ha sido notificado para valorar el producto."
        else:
            return f"Error al notificar al cliente para valorar el producto: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"

def leer_DB_valoraciones(ruta_archivo):
    base_datos_valoraciones = Graph()
    try:
        base_datos_valoraciones.parse(ruta_archivo, format="xml")
    except Exception as e:
        print("Error:", e)
    return base_datos_valoraciones


# Función para añadir una valoración a la base de datos RDF
def añadir_valoracion(usuario_id, producto_uri, valoracion, comentario):
    base_datos_valoraciones = leer_DB_valoraciones(archivo_valoraciones)

    # Generar un identificador único para la valoración
    valoracion_id = str(uuid.uuid4())

    valoracion_uri = ns[f"Valoracio_{valoracion_id}"]
    base_datos_valoraciones.add((valoracion_uri, RDF.type, ns.Valoracio))
    base_datos_valoraciones.add((valoracion_uri, ns.Usuari, Literal(usuario_id)))
    base_datos_valoraciones.add((valoracion_uri, ns.Producte, Literal(producto_uri)))
    base_datos_valoraciones.add((valoracion_uri, ns.Valoracio, Literal(valoracion, datatype=XSD.integer)))
    base_datos_valoraciones.add((valoracion_uri, ns.Comentari, Literal(comentario)))

    base_datos_valoraciones.serialize(destination=archivo_valoraciones, format="xml")


@app.route('/guardar_valoracion', methods=['POST'])
def guardar_valoracion():
    if request.method == 'POST':
        data = request.json
        usuario_id = "pepo"
        producto_uri = "hipopotamo"
        # usuario_id = data['usuario_id']
        # producto_uri = data['producto_uri']
        valoracion = data['valoracion']
        comentario = data['comentario']

        añadir_valoracion(usuario_id, producto_uri, valoracion, comentario)

        return "Valoración guardada correctamente en la base de datos RDF", 200
    else:
        return "Error: La solicitud debe ser POST", 400





  


# Función para leer la base de datos RDF de compras
def leer_DB_compras(ruta_archivo):
    base_datos_compras = Graph()
    try:
        base_datos_compras.parse(ruta_archivo, format="xml")
    except Exception as e:
        print("Error:", e)
    return base_datos_compras

# Función para consultar los productos comprados por un usuario
def consultar_productos_comprados(usuario_id):
    base_datos_compras = leer_DB_compras(archivo_compras)

    query = f"""
        PREFIX ns1: <http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#>
        SELECT ?producto
        WHERE {{
            ?producto ns1:Usuari "{usuario_id}" .
        }}
    """
    result = base_datos_compras.query(query)
    productos_comprados = [str(row[0]) for row in result]
    return productos_comprados

# Ruta para obtener los productos comprados por un usuario
@app.route('/productos_comprados/<usuario_id>', methods=['GET'])
def obtener_productos_comprados(usuario_id):
    productos_comprados = consultar_productos_comprados(usuario_id)
    if productos_comprados:
        return jsonify({"productos_comprados": productos_comprados})
    else:
        return jsonify({"mensaje": "No se encontraron productos comprados para el usuario"}), 404






def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'AgentValoracions',
        'location': 'http://localhost:5005'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')
      

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5005)