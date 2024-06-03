from flask import Flask, request, render_template, redirect, url_for, jsonify
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests
import datetime
import random


app = Flask(__name__)

ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

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
        print(f"Carrito recibido: {carrito}")
        print(f"Usuario recibido: {usuario_id}")

        if not carrito:
            print("El carrito está vacío")
            return jsonify({"error": "El carrito está vacío"}), 400

        noms = [producto['nombre'] for producto in carrito]
        preus = [producto['precio'] for producto in carrito]
        print(f"Nombres de productos: {noms}")
        print(f"Precios de productos: {preus}")

        insertar_compra(noms, preus, usuario_id)

        return jsonify({"message": "Compra registrada con éxito"}), 200
    except Exception as e:
        print(f"Error en el procesamiento de la compra: {e}")
        return jsonify({"error": str(e)}), 500    


def insertar_compra(noms, preus, usuario_id):
    base_datos = leer_DB("../data/compres.rdf")

    # Asegurarse de que las listas tengan la misma longitud
    if len(noms) != len(preus):
        print("Error: Las listas de nombres, cantidades y precios no tienen la misma longitud")
        return

    # Generar un identificador único para la compra
    compra_id = str(datetime.datetime.now().timestamp()).replace(".", "_")

    preuTotal = sum(preus)
    # Insertar cada producto en la base de datos
    for i, (nom, preu) in enumerate(zip(noms, preus), start=1):
        # Generar una URI única para el producto en esta compra
        product_uri = ns[f"Compra_{compra_id}_Producte{i}_{nom.replace(' ', '_')}"]

        # Añadir el producto a la base de datos
        base_datos.add((product_uri, RDF.type, ns.Compra))
        base_datos.add((product_uri, ns.Nom, Literal(nom)))
        base_datos.add((product_uri, ns.Quantitat, Literal(quantitat)))
        base_datos.add((product_uri, ns.Preu, Literal(preu, datatype=XSD.float)))
        base_datos.add((product_uri, ns.Usuari, Literal(usuario_id)))

    compra_uri = ns[f"Compra_{compra_id}"]
    base_datos.add((compra_uri, RDF.type, ns.Compra))
    base_datos.add((compra_uri, ns.PreuTotal, Literal(preuTotal, datatype=XSD.float)))
    base_datos.add((compra_uri, ns.Usuari, Literal(usuario_id)))
    
    # Guardar los cambios en la base de datos
    base_datos.serialize(destination="../data/compres.rdf", format="xml")

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

