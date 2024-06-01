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

# Ruta principal para recibir el JSON y procesarlo
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        num_productos = 4
        noms = generar_noms(num_productos)
        quantitats = generar_quantitats(num_productos)

        insertar_compra(noms, quantitats)

        return """Compra registrada con éxito <br>
            <a href="/">Añadir Nuevo Producto</a>
            """
        
    else:
        html = """
        <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Afegir Compra</title>
            </head>
            <body>
                <h1>Afegir Compra</h1>
                <form method="post">
                    <input type="submit" value="Afegir Compra">
                </form>
            </body>
            </html>
        """
        return html

def insertar_compra(noms, quantitats):
    base_datos = leer_DB("../data/compres.rdf")

    # Asegurarse de que las listas tengan la misma longitud
    if len(noms) != len(quantitats):
        print("Error: Las listas de nombres y cantidades no tienen la misma longitud")
        return

    # Generar un identificador único para la compra
    compra_id = str(datetime.datetime.now().timestamp()).replace(".", "_")

    # Insertar cada producto en la base de datos
    for i, (nom, quantitat) in enumerate(zip(noms, quantitats), start=1):
        # Generar una URI única para el producto en esta compra
        product_uri = ns[f"Compra_{compra_id}_Producte{i}_{nom.replace(' ', '_')}"]

        # Añadir el producto a la base de datos
        base_datos.add((product_uri, RDF.type, ns.Compra))
        base_datos.add((product_uri, ns.Nom, Literal(nom)))
        base_datos.add((product_uri, ns.Quantitat, Literal(quantitat)))

    # Guardar los cambios en la base de datos
    base_datos.serialize(destination="../data/compres.rdf", format="xml")


# Generar nombres ficticios para productos
def generar_noms(num_productos):
    noms = []
    for i in range(1, num_productos + 1):
        noms.append(f"Producte{i}")
    return noms

# Generar cantidades ficticias para productos
def generar_quantitats(num_productos):
    return [random.randint(1, 10) for _ in range(num_productos)]

# Ejemplo de uso
num_productos = 5
noms = generar_noms(num_productos)
quantitats = generar_quantitats(num_productos)

# Imprimir los nombres y cantidades generadas
for nom, quantitat in zip(noms, quantitats):
    print(f"Nom: {nom}, Quantitat: {quantitat}")


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

