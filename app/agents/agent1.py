from flask import Flask, request, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid

app = Flask(__name__, template_folder='templates')

# Definir el namespace
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

# Función para leer el archivo RDF
def leer_DB(ruta_archivo):
    g = Graph()
    try:
        g.parse(ruta_archivo, format="xml")
        num_tripletas = len(g)
        print(f"Se han cargado {num_tripletas} tripletas desde el archivo RDF.")
    except Exception as e:
        print("Error:", e)
    return g

# Función para guardar el archivo RDF
def guardar_DB(base_datos, ruta_archivo):
    base_datos.serialize(destination=ruta_archivo, format="xml")

# Función para añadir un nuevo producto
def añadir_producto(base_datos, nombre_producto, marca, modelo, precio, peso):
    product_uri = ECSDI['Producto_' + str(uuid.uuid4())]

    base_datos.add((product_uri, RDF.type, ECSDI.Producto))
    base_datos.add((product_uri, ECSDI.Nombre, Literal(nombre_producto, datatype=XSD.string)))
    base_datos.add((product_uri, ECSDI.Marca, Literal(marca, datatype=XSD.string)))
    base_datos.add((product_uri, ECSDI.Modelo, Literal(modelo, datatype=XSD.string)))
    base_datos.add((product_uri, ECSDI.Precio, Literal(precio, datatype=XSD.float)))
    base_datos.add((product_uri, ECSDI.Peso, Literal(peso, datatype=XSD.float)))

# Ruta al archivo RDF
archivo_base_datos = "../data/productes.rdf"

@app.route('/')
def home():
    html = """
        <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Añadir Nuevo Producto</title>
    </head>
    <body>
        <h1>Añadir Nuevo Producto</h1>
        <form method="post">
            <label for="nombre">Nombre:</label>
            <input type="text" id="nombre" name="nombre" required><br>
            <label for="marca">Marca:</label>
            <input type="text" id="marca" name="marca" required><br>
            <label for="modelo">Modelo:</label>
            <input type="text" id="modelo" name="modelo" required><br>
            <label for="precio">Precio:</label>
            <input type="number" step="0.01" id="precio" name="precio" required><br>
            <label for="peso">Peso:</label>
            <input type="number" step="0.01" id="peso" name="peso" required><br>
            <input type="submit" value="Añadir Producto">
        </form>
    </body>
    </html>
    """
    return html

@app.route('/newProduct', methods=['GET', 'POST'])
def new_product():
    if request.method == 'POST':
        nombre_producto = request.form['nombre']
        marca = request.form['marca']
        modelo = request.form['modelo']
        precio = float(request.form['precio'])
        peso = float(request.form['peso'])

        base_datos = leer_DB(archivo_base_datos)
        añadir_producto(base_datos, nombre_producto, marca, modelo, precio, peso)
        guardar_DB(base_datos, archivo_base_datos)

        return redirect(url_for('home'))

    return render_template('addProduct.html')


if __name__ == "__main__":
    app.run(port=5001)