from flask import Flask, request, jsonify, render_template
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF
import requests, random
import json
import time
import threading

app = Flask(__name__)

base_datos_productes = "../data/productes.rdf"
base_datos_productesCercats = "../data/productesCercats.rdf"
base_datos_compras = "../data/compres.rdf"
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
CLIENT_URL = 'http://localhost:5007'

def leer_DB(ruta_archivo):
    base_datos = Graph()

    try:
        base_datos.parse(ruta_archivo, format="xml")
        print("Productos en la base de datos productesRDF:")

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

def leer_DB_productes_cercats(ruta_archivo):
    base_datos = Graph()

    try:
        base_datos.parse(ruta_archivo, format="xml")
        print("Productos cercados en la base de datos productesCercats:")

        for producto_cercat in base_datos.subjects(RDF.type, ECSDI.CercaUsuari):
            nombre_producto = base_datos.value(producto_cercat, ECSDI.ProducteCercat)
            usuario = base_datos.value(producto_cercat, ECSDI.Usuario)
            print(f" Producto Cercado: {nombre_producto}")
            print(f"  Usuario: {usuario}")
            print("---")

    except Exception as e:
        print("Error:", e)

    return base_datos

def leer_DB_compras(ruta_archivo):
    base_datos = Graph()

    try:
        base_datos.parse(ruta_archivo, format="xml")
        print("Productos cercados en la base de datos productesCercats:")

        for producto_cercat in base_datos.subjects(RDF.type, ECSDI.Compra):
            nombre_producto = base_datos.value(producto_cercat, ECSDI.Producto)
            usuario = base_datos.value(producto_cercat, ECSDI.Usuario)
            print(f" Producto Comprado: {nombre_producto}")
            print(f"  Usuario: {usuario}")
            print("---")

    except Exception as e:
        print("Error:", e)

    return base_datos

@app.route('/', methods=['GET', 'POST'])
def home():
    return """
        <h1>Bienvenido al agente recomendador</h1>
        <form action="/EnviarRecomanacio" method="post">
            <input type="submit" value="Iniciar Recomanació">
        </form>
        """

@app.route("/EnviarRecomanacio", methods=['POST'])
def enviar_recomanacio():
    #usuario = "Sergi"
    data = request.get_json()
    usuario = str(data.get('nombre'))
    print(f"Nom usuairo  obtingut: {usuario}")

    try:
        base_datos_cercats = leer_DB_productes_cercats(base_datos_productesCercats)
        #base_datos_compras = leer_DB_compras(base_datos_compras)
        base_datos_productos = leer_DB(base_datos_productes)
    except Exception as e:
        return f"Error al leer la base de datos: {e}", 500

    if usuario:
        productos_cercats_usuario = []

        #Busca a compres
        for producto in base_datos_cercats.subjects(RDF.type, ECSDI.CercaUsuari):
            user_bd = base_datos_cercats.value(producto, ECSDI.Usuario)
            if str(usuario) == str(user_bd):
                nombre_producto = base_datos_cercats.value(producto, ECSDI.ProducteCercat)
                productos_cercats_usuario.append(str(nombre_producto))

        #Busca a compres
        '''
        for producto in base_datos_compras.subjects(RDF.type, ECSDI.Compra):
            user_bd = base_datos_compras.value(producto, ECSDI.Usuario)
            if str(usuario) == str(user_bd):
                nombre_producto = base_datos_cercats.value(producto, ECSDI.Producto)
                productos_cercats_usuario.append(str(nombre_producto))'''

        if not productos_cercats_usuario:
            return jsonify({"error": "No se encontraron productos cercados para el usuario proporcionado"}), 404

        # Buscar productos recomendados basados en la categoría de los productos cercados
        productos_recomendados = []

        for nombre_producto in productos_cercats_usuario:
            for producto in base_datos_productos.subjects(RDF.type, ECSDI.Producte):
                nombre = base_datos_productos.value(producto, ECSDI.Nom)
                categoria = base_datos_productos.value(producto, ECSDI.Categoria)

                if nombre_producto.lower() in str(nombre).lower():
                    for producto_recomendado in base_datos_productos.subjects(RDF.type, ECSDI.Producte):
                        if producto != producto_recomendado:
                            categoria_recomendada = base_datos_productos.value(producto_recomendado, ECSDI.Categoria)
                            if str(categoria).lower() == str(categoria_recomendada).lower():
                                productos_recomendados.append(producto_recomendado)

        if not productos_recomendados:
            return jsonify({"error": "No se encontraron productos recomendados"}), 404

        # Seleccionar el primer producto recomendado (o aplicar alguna otra lógica de selección)
        #producto_recomendar = productos_recomendados[0]
        producto_recomendar = random.choice(productos_recomendados)
        producto_info_a_enviar = {
            'nombre': str(base_datos_productos.value(producto_recomendar, ECSDI.Nom)),
            'precio': float(base_datos_productos.value(producto_recomendar, ECSDI.Preu)),
            'categoria': str(base_datos_productos.value(producto_recomendar, ECSDI.Categoria)),
            'descripcion': str(base_datos_productos.value(producto_recomendar, ECSDI.Descripcio)),
            'num_valoraciones': int(base_datos_productos.value(producto_recomendar, ECSDI.NumValoracions)),
            'estrellas_mitges': float(base_datos_productos.value(producto_recomendar, ECSDI.EstrellesMitges))
        }

        print(f"Info de producte a recomendar: {producto_info_a_enviar}")

        return jsonify(producto_info_a_enviar)

    else:
        return jsonify({"error": "Debe proporcionar el ID del usuario en el cuerpo del mensaje."}), 400

'''def enviar_recomendaciones_periodicamente():
    while True:
        try:
            response = requests.post("http://localhost:5010/EnviarRecomanacio", json={"usuario_id": "Sergi"})
            print(f"Recomendación enviada: {response.status_code}")
        except Exception as e:
            print(f"Error al enviar la recomendación: {e}")

        time.sleep(5000)'''

def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'AgentRecomanador',
        'location': 'http://localhost:5010'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')

if __name__ == "__main__":
    register_with_directory()
    #threading.Thread(target=enviar_recomendaciones_periodicamente, daemon=True).start()
    app.run(port=5010)
