import uuid

import requests
from flask import Flask, jsonify, request
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

app = Flask(__name__)

ns = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

archivo_base_datos = "../data/factures.rdf"


@app.route('/')
def home():
    return "<h1>Bienvenido al agente tresorer</h1>"


@app.route('/CrearFactura', methods=['POST'])
def procesar_pedido():
    try:
        data = request.get_json()
        carrito = data['carrito']
        direccion = data['direccion']
        totalPreu = data['totalPreu']

        print(f"Pedido recibido: {carrito}")
        print(f"Dirección de entrega: {direccion}")
        print(f"Precio total: {totalPreu}")

        usuario_id = 'Antonio'
        facturaPagada = False
        guardar_factura(carrito, usuario_id, direccion,
                        totalPreu, facturaPagada)

        lca_url = 'http://localhost:5007/posarFactura'

        response = requests.post(lca_url, json=data)
        if response.status_code == 200:
            print("Factura creada con éxito")
            return jsonify({"message": "Factura creada con exito"}), 200
        else:
            print("Error al notificar al centro logístico")

    except Exception as e:
        print(f"Error en el procesamiento del pedido: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/NotifyClient', methods=['POST'])
def notify_client():
    try:
        data = request.get_json()
        nombre_producto = data['nombre_producto']
        direccion = data['direccion']
        price = data['price']
        time_of_delivery = data['time_of_delivery']
        delivery_guy = data['delivery_guy']

        # Log the notification details
        print(f"Notificación recibida para el producto {nombre_producto}")
        print(f"Dirección de entrega: {direccion}")
        print(f"Precio: {price}")
        print(f"Tiempo de entrega estimado: {time_of_delivery}")
        print(f"Repartidor: {delivery_guy}")

        # Process the notification (e.g., update the database, send an email, etc.)

        return jsonify({"message": "Notificación recibida"}), 200
    except Exception as e:
        print(f"Error al recibir la notificación: {e}")
        return jsonify({"error": str(e)}), 500


def leer_DB(ruta_archivo):
    base_datos = Graph()
    try:
        base_datos.parse(ruta_archivo, format="xml")
    except Exception as e:
        print("Error:", e)
    return base_datos


def guardar_factura(carrito, usuario_id, direccion, preuTotal, facturaPagada):
    base_datos = leer_DB(archivo_base_datos)
    print(f"Carrito: {carrito}")
    print(f"  Usuario ID: {usuario_id}")
    print(f"  Dirección: {direccion}")
    print(f"  Precio Total: {preuTotal}")
    print(f"  Factura Pagada: {facturaPagada}")
    print("---")

    factura_id = f"Factura_{uuid.uuid4()}"
    factura_uri = ns[factura_id]

    base_datos.add((factura_uri, RDF.type, ns.Factura))
    base_datos.add((factura_uri, ns.Usuario, Literal(usuario_id)))
    base_datos.add((factura_uri, ns.Direccion, Literal(direccion)))
    base_datos.add((factura_uri, ns.PrecioTotal,
                   Literal(preuTotal, datatype=XSD.float)))
    base_datos.add((factura_uri, ns.FacturaPagada, Literal(
        facturaPagada, datatype=XSD.boolean)))

    for producto in carrito:
        producto_uri = ns[f"Producto_{producto['nombre'].replace(' ', '_')}"]
        base_datos.add((producto_uri, RDF.type, ns.Producto))
        base_datos.add((producto_uri, ns.Nombre, Literal(producto['nombre'])))
        base_datos.add((producto_uri, ns.Descripcion,
                       Literal(producto['descripcion'])))
        base_datos.add((producto_uri, ns.Categoria,
                       Literal(producto['categoria'])))
        base_datos.add((producto_uri, ns.Precio, Literal(
            producto['precio'], datatype=XSD.float)))

        # Relacionar producto con factura
        base_datos.add((factura_uri, ns.Producto, producto_uri))

    base_datos.serialize(destination=archivo_base_datos, format="xml")
    print(f"Factura {factura_id} guardada correctamente.")


def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'AgentTresorer',
        'location': 'http://localhost:5008'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')


if __name__ == "__main__":
    register_with_directory()
    app.run(port=5008)
