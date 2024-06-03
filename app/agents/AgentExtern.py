from flask import Flask, request, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests
import datetime


app = Flask(__name__)

archivo_base_datos = "../data/productes.rdf"

# Definir el namespace
ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
  

# Función para leer la base de datos RDF
def leer_DB(ruta_archivo):
    base_datos = Graph()
    try:
        base_datos.parse(ruta_archivo, format="xml")
    except Exception as e:
        print("Error:", e)
    return base_datos

# Función para añadir un producto a la base de datos RDF
def añadir_producto(nom, preu, categoria, descripcio, numValoracions, estrellesMitges):
    base_datos = leer_DB(archivo_base_datos)
    print(f"Producto: {nom}")
    print(f"  Precio: {preu}")
    print(f"  Categoría: {categoria}")
    print(f"  Descripción: {descripcio}")
    print(f"  Número de Valoraciones: {numValoracions}")
    print(f"  Estrellas Medias: {estrellesMitges}")
    print("---")

    product_uri = ns["Producte_" + nom.replace(" ", "_")]  # Generar URI única para el producto
    base_datos.add((product_uri, RDF.type, ns.Producte))
    base_datos.add((product_uri, ns.Nom, Literal(nom)))
    base_datos.add((product_uri, ns.Preu, Literal(preu)))
    base_datos.add((product_uri, ns.Categoria, Literal(categoria)))
    base_datos.add((product_uri, ns.Descripcio, Literal(descripcio)))
    base_datos.add((product_uri, ns.NumValoracions, Literal(numValoracions)))
    base_datos.add((product_uri, ns.EstrellesMitges, Literal(estrellesMitges)))

    base_datos.serialize(destination=archivo_base_datos, format="xml")

@app.route('/external_products', methods=['POST'])
def external_products():
    data = request.json
    nom = data['nom']
    preu = data['preu']
    categoria = data['categoria']
    descripcio = data['descripcio']
    numValoracions = data['numValoracions']
    estrellesMitges = data['estrellesMitges']

    añadir_producto(nom, preu, categoria, descripcio, numValoracions, estrellesMitges)

    return "Producto añadido correctamente a la base de datos RDF", 200


@app.route('/')
def home():
    return "<h1>Bienvenido al agente extern</h1>"
      

def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'AgentExtern',
        'location': 'http://localhost:5004'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')
      

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5004)
