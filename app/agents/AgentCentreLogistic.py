import os
import uuid

import requests
from flask import Flask, jsonify, render_template, request
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

app = Flask(__name__)

ns = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

# Paths for RDF databases
transport_agency_db_path = "../data/pedidos.rdf"
pedidos_db_path = "../data/pedidos.rdf"
stock_db_path = "../data/stock.rdf"

client_agent_url = 'http://localhost:5008/NotifyClient'
ta_url = 'http://localhost:5014/GetOffer'


def leer_DB(ruta_archivo):
    g = Graph()
    try:
        g.parse(ruta_archivo, format="xml")
    except Exception as e:
        print("Error:", e)
    return g


def inicializar_transport_agency_db():
    g = Graph()
    if os.path.exists(transport_agency_db_path):
        g.parse(transport_agency_db_path, format="xml")

    # Check if the TA is already in the database
    existing_ta = None
    for ta in g.subjects(RDF.type, ns.TransportAgency):
        url = str(g.value(ta, ns.url))
        if url == ta_url:
            existing_ta = ta
            break

    if existing_ta is None:
        print("Adding Transport Agency to the DB...")
        ta_id = str(uuid.uuid4())
        ta_uri = ns[f"TransportAgency_{ta_id}"]
        g.add((ta_uri, RDF.type, ns.TransportAgency))
        g.add((ta_uri, ns.url, Literal(ta_url, datatype=XSD.string)))
        g.serialize(destination=transport_agency_db_path, format="xml")
        print("Transport Agency added to the DB.")
    else:
        print("Transport Agency already exists in the DB.")


def register_with_directory(agent_name, agent_location):
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': agent_name,
        'location': agent_location
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print(f'{agent_name} registered successfully with the directory')
    else:
        print(f'Failed to register {agent_name} with the directory')


@app.route('/')
def home():
    return "<h1>Bienvenido al Centro Logístico</h1>"


@app.route('/CrearProducto', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        guardar_producto(nombre, cantidad)
        return jsonify({"message": "Producto creado con éxito"}), 200
    return render_template('crear_producto.html')


def guardar_producto(nombre, cantidad):
    base_datos = leer_DB(stock_db_path)

    product_id = str(uuid.uuid4())
    product_uri = ns[f"Producto_{product_id}"]
    base_datos.add((product_uri, RDF.type, ns.Producto))
    base_datos.add(
        (product_uri, ns.nombre, Literal(nombre, datatype=XSD.string)))
    base_datos.add((product_uri, ns.cantidad,
                   Literal(cantidad, datatype=XSD.int)))

    base_datos.serialize(destination=stock_db_path, format="xml")
    print("Producto guardado correctamente")


@app.route('/VerificarProducto', methods=['POST'])
def verificar_producto():
    try:
        data = request.get_json()
        nombre_producto = data['nombre_producto']
        disponible = verificar_disponibilidad(nombre_producto)
        return jsonify({"nombre_producto": nombre_producto, "disponible": disponible}), 200
    except Exception as e:
        print(f"Error al verificar el producto: {e}")
        return jsonify({"error": str(e)}), 500


def verificar_disponibilidad(nombre_producto):
    base_datos = leer_DB(stock_db_path)
    productos = base_datos.subjects(
        predicate=ns.nombre, object=Literal(nombre_producto, datatype=XSD.string))
    for producto in productos:
        cantidad = base_datos.value(subject=producto, predicate=ns.cantidad)
        if int(cantidad) > 0:
            return True
    return False


@app.route('/PrepararEnvio', methods=['POST'])
def preparar_envio():
    try:
        data = request.get_json()
        nombre_producto = data['nombre_producto']
        direccion = data['direccion']
        print(f"Preparando envío para el producto: {
              nombre_producto} a la dirección: {direccion}")

        if decrementar_stock(nombre_producto):
            guardar_pedido(nombre_producto, direccion)
            return jsonify({"message": "Producto preparado para envío"}), 200
        else:
            return jsonify({"error": "Stock insuficiente"}), 400
    except Exception as e:
        print(f"Error al preparar el envío: {e}")
        return jsonify({"error": str(e)}), 500


def decrementar_stock(nombre_producto):
    base_datos = leer_DB(stock_db_path)
    productos = base_datos.subjects(
        predicate=ns.nombre, object=Literal(nombre_producto, datatype=XSD.string))
    for producto in productos:
        cantidad = int(base_datos.value(
            subject=producto, predicate=ns.cantidad))
        if cantidad > 0:
            nueva_cantidad = cantidad - 1
            base_datos.set((producto, ns.cantidad, Literal(
                nueva_cantidad, datatype=XSD.int)))
            base_datos.serialize(destination=stock_db_path, format="xml")
            return True
    return False


def guardar_pedido(nombre_producto, direccion):
    base_datos = leer_DB(pedidos_db_path)

    pedido_id = str(uuid.uuid4())
    pedido_uri = ns[f"Pedido_{pedido_id}"]
    base_datos.add((pedido_uri, RDF.type, ns.Pedido))
    base_datos.add((pedido_uri, ns.nombre_producto, Literal(
        nombre_producto, datatype=XSD.string)))
    base_datos.add((pedido_uri, ns.direccion, Literal(
        direccion, datatype=XSD.string)))

    base_datos.serialize(destination=pedidos_db_path, format="xml")
    print("Pedido guardado correctamente")


@app.route('/EnviarPedidos', methods=['POST', 'GET'])
def enviar_pedidos():
    try:
        organizar_lotes()
        return jsonify({"message": "Pedidos organizados y listos para envío"}), 200
    except Exception as e:
        print(f"Error al enviar los pedidos: {e}")
        return jsonify({"error": str(e)}), 500


def organizar_lotes():
    base_datos = leer_DB(pedidos_db_path)
    pedidos = {}
    for pedido in base_datos.subjects(RDF.type, ns.Pedido):
        direccion = str(base_datos.value(pedido, ns.direccion))
        # Assume last word in the address is the city
        ciudad = direccion.split()[-1]
        if ciudad not in pedidos:
            pedidos[ciudad] = []
        pedidos[ciudad].append(pedido)

    for ciudad, productos in pedidos.items():
        print(f"Lote para {ciudad}:")
        for producto in productos:
            nombre_producto = str(base_datos.value(
                producto, ns.nombre_producto))
            print(f" - {nombre_producto}")

        # Request offers for the lot
        ofertas = solicitar_ofertas(ciudad)
        if ofertas:
            mejor_oferta = min(ofertas, key=lambda x: x['price'])
            print(f"Mejor oferta: {mejor_oferta}")
            # Notify the client and delete the products from the products to send
            for producto in productos:
                nombre_producto = str(base_datos.value(
                    producto, ns.nombre_producto))
                direccion = str(base_datos.value(producto, ns.direccion))
                notificar_cliente(nombre_producto, direccion, mejor_oferta)
                eliminar_pedido(producto)


def solicitar_ofertas(ciudad):
    agencias = obtener_agencias_transporte()
    ofertas = []
    for agencia in agencias:
        try:
            response = requests.post(agencia, json={"city": ciudad})
            if response.status_code == 200:
                oferta = response.json()
                ofertas.append(oferta)
        except Exception as e:
            print(f"Error al solicitar oferta de {agencia}: {e}")
    return ofertas


def obtener_agencias_transporte():
    base_datos = leer_DB(transport_agency_db_path)
    agencias = []
    for agencia in base_datos.subjects(RDF.type, ns.TransportAgency):
        url = str(base_datos.value(agencia, ns.url))
        agencias.append(url)
    return agencias


def notificar_cliente(nombre_producto, direccion, mejor_oferta):
    notificacion = {
        "nombre_producto": nombre_producto,
        "direccion": direccion,
        "price": mejor_oferta['price'],
        "time_of_delivery": mejor_oferta['time_of_delivery'],
        "delivery_guy": mejor_oferta['delivery_guy']
    }
    try:
        response = requests.post(client_agent_url, json=notificacion)
        if response.status_code == 200:
            print(f"Cliente notificado sobre el producto {nombre_producto}")
        else:
            print(f"Error al notificar al cliente sobre el producto {
                  nombre_producto}")
    except Exception as e:
        print(f"Error al notificar al cliente: {e}")


def eliminar_pedido(pedido_uri):
    base_datos = leer_DB(pedidos_db_path)
    base_datos.remove((pedido_uri, None, None))
    base_datos.serialize(destination=pedidos_db_path, format="xml")
    print("Pedido eliminado correctamente")


if __name__ == "__main__":
    inicializar_transport_agency_db()
    register_with_directory('LogisticCenterAgent', 'http://localhost:5012')
    app.run(port=5012)
