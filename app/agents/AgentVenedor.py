import datetime
import uuid

import requests
from flask import Flask, jsonify, request
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

app = Flask(__name__)

ns = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")


def leer_DB(ruta_archivo):
    g = Graph()
    try:
        g.parse(ruta_archivo, format="xml")
    except Exception as e:
        print("Error:", e)
    return g


@app.route('/')
def home():
    return "<h1>Bienvenido al agente venedor</h1>"


@app.route('/ProcesarCompra', methods=['POST'])
def procesar_compra():
    try:
        data = request.get_json()
        carrito = data['carrito']
        usuario_id = data['usuario_id']
        direccion = data['direccion']
        print(f"Carrito recibido: {carrito}")
        print(f"Usuario recibido: {usuario_id}")
        print(f"Dirección recibida: {direccion}")

        if not carrito:
            print("El carrito está vacío")
            return jsonify({"error": "El carrito está vacío"}), 400

        noms = [producto['nombre'] for producto in carrito]
        preus = [producto['precio'] for producto in carrito]
        print(f"Nombres de productos: {noms}")
        print(f"Precios de productos: {preus}")

        insertar_compra(noms, preus, usuario_id, direccion)
        notificar_centro_logistico(carrito, direccion)

        return jsonify({"message": "Compra registrada con éxito"}), 200
    except Exception as e:
        print(f"Error en el procesamiento de la compra: {e}")
        return jsonify({"error": str(e)}), 500


def insertar_compra(noms, preus, usuario_id, direccion):
    base_datos = leer_DB("../data/compres.rdf")

    if len(noms) != len(preus):
        print("Las listas de nombres y precios tienen diferentes longitudes")
        return

    compra_id = str(uuid.uuid4())
    compra_uri = ns[f"Compra_{compra_id}"]
    base_datos.add((compra_uri, RDF.type, ns.Compra))
    base_datos.add((compra_uri, ns.id_usuario, Literal(
        usuario_id, datatype=XSD.string)))
    base_datos.add((compra_uri, ns.fecha, Literal(
        datetime.datetime.now(), datatype=XSD.dateTime)))
    base_datos.add((compra_uri, ns.direccion, Literal(
        direccion, datatype=XSD.string)))

    for nom, preu in zip(noms, preus):
        producte_id = str(uuid.uuid4())
        producte_uri = ns[f"Compra_{compra_id}_Producte_{producte_id}"]
        base_datos.add((producte_uri, RDF.type, ns.Producte))
        base_datos.add(
            (producte_uri, ns.nom, Literal(nom, datatype=XSD.string)))
        base_datos.add(
            (producte_uri, ns.preu, Literal(preu, datatype=XSD.float)))
        base_datos.add((compra_uri, ns.conté, producte_uri))

    base_datos.serialize(destination="../data/compres.rdf", format="xml")
    print("Compra insertada correctamente")


def notificar_centro_logistico(carrito, direccion):
    lca_url = 'http://localhost:5013/ProcesarPedido'
    data = {
        "carrito": carrito,
        "direccion": direccion
    }
    response = requests.post(lca_url, json=data)
    if response.status_code == 200:
        print("Notificación al centro logístico exitosa")
    else:
        print("Error al notificar al centro logístico")


def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'SellerAgent',
        'location': 'http://localhost:5003'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')


if __name__ == "__main__":
    register_with_directory()
    app.run(port=5003)
