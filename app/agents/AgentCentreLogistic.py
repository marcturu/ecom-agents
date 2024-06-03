import uuid

from flask import Flask, jsonify, render_template, request
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
    base_datos = leer_DB("../data/stock.rdf")

    product_id = str(uuid.uuid4())
    product_uri = ns[f"Producto_{product_id}"]
    base_datos.add((product_uri, RDF.type, ns.Producto))
    base_datos.add(
        (product_uri, ns.nombre, Literal(nombre, datatype=XSD.string)))
    base_datos.add((product_uri, ns.cantidad,
                   Literal(cantidad, datatype=XSD.int)))

    base_datos.serialize(destination="../data/stock.rdf", format="xml")
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
    base_datos = leer_DB("../data/stock.rdf")
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
    base_datos = leer_DB("../data/stock.rdf")
    productos = base_datos.subjects(
        predicate=ns.nombre, object=Literal(nombre_producto, datatype=XSD.string))
    for producto in productos:
        cantidad = int(base_datos.value(
            subject=producto, predicate=ns.cantidad))
        if cantidad > 0:
            nueva_cantidad = cantidad - 1
            base_datos.set((producto, ns.cantidad, Literal(
                nueva_cantidad, datatype=XSD.int)))
            base_datos.serialize(destination="../data/stock.rdf", format="xml")
            return True
    return False


def guardar_pedido(nombre_producto, direccion):
    base_datos = leer_DB("../data/pedidos.rdf")

    pedido_id = str(uuid.uuid4())
    pedido_uri = ns[f"Pedido_{pedido_id}"]
    base_datos.add((pedido_uri, RDF.type, ns.Pedido))
    base_datos.add((pedido_uri, ns.nombre_producto, Literal(
        nombre_producto, datatype=XSD.string)))
    base_datos.add((pedido_uri, ns.direccion, Literal(
        direccion, datatype=XSD.string)))

    base_datos.serialize(destination="../data/pedidos.rdf", format="xml")
    print("Pedido guardado correctamente")


@app.route('/EnviarPedidos', methods=['POST'])
def enviar_pedidos():
    try:
        organizar_lotes()
        return jsonify({"message": "Pedidos organizados y listos para envío"}), 200
    except Exception as e:
        print(f"Error al enviar los pedidos: {e}")
        return jsonify({"error": str(e)}), 500


def organizar_lotes():
    base_datos = leer_DB("../data/pedidos.rdf")
    pedidos = {}
    for pedido in base_datos.subjects(RDF.type, ns.Pedido):
        direccion = str(base_datos.value(pedido, ns.direccion))
        if direccion not in pedidos:
            pedidos[direccion] = []
        pedidos[direccion].append(pedido)

    for direccion, productos in pedidos.items():
        print(f"Lote para {direccion}:")
        for producto in productos:
            nombre_producto = str(base_datos.value(
                producto, ns.nombre_producto))
            print(f" - {nombre_producto}")


if __name__ == "__main__":
    app.run(port=5012)
