from flask import Flask, request, render_template, redirect, url_for, jsonify
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests
import json

app = Flask(__name__)

AGENTE_CLIENT_URL = 'http://localhost:5007/ElegirProducte'


base_datos_productos = "../data/productes.rdf"
base_datos_productesCercats = "../data/productesCercats.rdf"
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

def leer_DB(ruta_archivo):
    base_datos = Graph()

    try:
        base_datos.parse(ruta_archivo, format="xml")
        print("Productos en la base de datos RDF:")

        # Iterar sobre todos los sujetos que son de tipo 'Producte'
        for producto in base_datos.subjects(RDF.type, ECSDI.Producte):
            nombre = base_datos.value(producto, ECSDI.Nom)
            precio = base_datos.value(producto, ECSDI.Preu)
            categoria = base_datos.value(producto, ECSDI.Categoria)
            descripcion = base_datos.value(producto, ECSDI.Descripcio)
            num_valoraciones = base_datos.value(producto, ECSDI.NumValoracions)
            estrellas_mitges = base_datos.value(producto, ECSDI.EstrellesMitges)

            print(f" Producto: {nombre}")
            print(f"  Precio: {precio}")
            print(f"  Categoría: {categoria}")
            print(f"  Descripción: {descripcion}")
            print(f"  Número de Valoraciones: {num_valoraciones}")
            print(f"  Estrellas Medias: {estrellas_mitges}")
            print("---")

    except Exception as e:
        print("Error:", e)

    return base_datos

def guardar_producto_cercat(nombre_producto, nombre_usuario):
    # Cargar la base de datos de productos cercados si no ha sido cargada previamente
    if not hasattr(guardar_producto_cercat, 'base_datos_productes_cercats'):
        guardar_producto_cercat.base_datos_productes_cercats = leer_DB(base_datos_productesCercats)

    # Crear una nueva URI para el producto
    producto_uri = ECSDI[f"Producte_{nombre_producto.replace(' ', '')}"]

    # Agregar tripleta a la base de datos
    guardar_producto_cercat.base_datos_productes_cercats.add((producto_uri, ECSDI.ProducteCercat, Literal(nombre_producto)))
    guardar_producto_cercat.base_datos_productes_cercats.add((producto_uri, ECSDI.Usuario, Literal(nombre_usuario)))

    # Guardar la base de datos en un archivo
    guardar_producto_cercat.base_datos_productes_cercats.serialize(destination="../data/productesCercats.rdf", format="xml")

    return

@app.route('/', methods=['GET', 'POST'])
def home():
    return "<h1>Bienvenido al agente dependiente</h1>"

@app.route("/FiltrarProducte", methods=['GET', 'POST'])
def cerca():

    data = request.get_json()
    print(f"Datos recibidos: {data}")

    filtros = {
        'nom': data.get('nom', ''),
        'preu_min': data.get('preu_min', ''),
        'preu_max': data.get('preu_max', ''),
        'categoria': data.get('categoria', ''),
        'num_valoracions_min': data.get('num_valoracions_min', ''),
        'estrelles_min': data.get('estrelles_min', '')
    }

    try:
        base_datos = leer_DB(base_datos_productos)
    except Exception as e:
        return f"Error al leer la base de datos: {e}", 500

    productos_filtrados_list = []

    for producto in base_datos.subjects(RDF.type, ECSDI.Producte):
        nombre = base_datos.value(producto, ECSDI.Nom)
        precio = base_datos.value(producto, ECSDI.Preu)
        categoria_producto = base_datos.value(producto, ECSDI.Categoria)
        descripcion = base_datos.value(producto, ECSDI.Descripcio)
        num_valoraciones = base_datos.value(producto, ECSDI.NumValoracions)
        estrellas_mitges = base_datos.value(producto, ECSDI.EstrellesMitges)

        if ((not filtros['nom'] or filtros['nom'].lower() in str(nombre).lower()) and
                (not filtros['preu_min'] or (precio and float(precio) >= float(filtros['preu_min']))) and
                (not filtros['preu_max'] or (precio and float(precio) <= float(filtros['preu_max']))) and
                (not filtros['categoria'] or filtros['categoria'].lower() in str(categoria_producto).lower()) and
                (not filtros['num_valoracions_min'] or (num_valoraciones and int(num_valoraciones) >= int(filtros['num_valoracions_min']))) and
                (not filtros['estrelles_min'] or (estrellas_mitges and int(estrellas_mitges) >= int(filtros['estrelles_min'])))):

            producto_filtrado = {
                'nombre': nombre if nombre else '',
                'precio': float(precio) if precio else 0.0,
                'categoria': categoria_producto if categoria_producto else '',
                'descripcion': descripcion if descripcion else '',
                'num_valoraciones': int(num_valoraciones) if num_valoraciones else 0,
                'estrellas_mitges': int(estrellas_mitges) if estrellas_mitges else 0
            }
            productos_filtrados_list.append(producto_filtrado)

    if productos_filtrados_list:
        return jsonify(productos_filtrados_list), 200
    else:
        return "No se encontraron productos que coincidan con los filtros proporcionados", 404


@app.route("/MostrarProducte", methods=['GET', 'POST'])
def mostrar():

    data = request.get_json()
    print(f"Datos recibidos: {data}")

    try:
        base_datos = leer_DB(base_datos_productos)
    except Exception as e:
        return f"Error al leer la base de datos: {e}", 500

    # Verificar si se proporcionó el nombre del producto seleccionado
    if 'nombre' in data:
        nom = data.get('nombre', '')
        usuari = data['usuario_id']
        if nom:
            guardar_producto_cercat(nom, usuari)

            # Recorrer la base de datos para encontrar la información del producto
            for producto in base_datos.subjects(RDF.type, ECSDI.Producte):
                nombre = base_datos.value(producto, ECSDI.Nom)
                if str(nombre) == str(nom):
                    precio = base_datos.value(producto, ECSDI.Preu)
                    categoria = base_datos.value(producto, ECSDI.Categoria)
                    descripcion = base_datos.value(producto, ECSDI.Descripcio)
                    num_valoraciones = base_datos.value(producto, ECSDI.NumValoracions)
                    estrellas_mitges = base_datos.value(producto, ECSDI.EstrellesMitges)

                    # Preparar la información del producto para la respuesta
                    producto_info = {
                        'Nom': nombre,
                        'Preu': float(precio) if precio else 0.0,
                        'Categoria': categoria if categoria else '',
                        'Descripcio': descripcion if descripcion else '',
                        'NumValoracions': int(num_valoraciones) if num_valoraciones else 0,
                        'EstrellesMitges': int(estrellas_mitges) if estrellas_mitges else 0
                    }

                    # Convertir los datos de producto_info a un formato JSON más común
                    producto_info_a_enviar = {
                        'Nom': str(producto_info['Nom']),
                        'Preu': float(producto_info['Preu']),
                        'Categoria': str(producto_info['Categoria']),
                        'Descripcio': str(producto_info['Descripcio']),
                        'NumValoracions': int(producto_info['NumValoracions']),
                        'EstrellesMitges': int(producto_info['EstrellesMitges'])
                    }

                    print(f"Info de producte individual a passar al Sergi: {producto_info_a_enviar}")
                    return jsonify(producto_info_a_enviar), 200

            return jsonify({"error": "Producto no encontrado"}), 404
    else:
        return jsonify({"error": "Debe proporcionar el nombre del producto seleccionado en el cuerpo del mensaje."}), 400


def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'AgentDependent',
        'location': 'http://localhost:5006'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5006)