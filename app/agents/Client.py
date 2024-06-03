import json
import uuid
from itertools import product

import requests
from flask import Flask, redirect, render_template, request, url_for
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD

app = Flask(__name__)

carritoCompra = []
precioTotal = 0.0

carritoGeneral = ""
direccioGeneral = ""
preuGeneral = 0.0

AGENTE_URL = 'http://localhost:5006/FiltrarProducte'
AGENTE_PRODUCTE_URL = 'http://localhost:5006/MostrarProducte'
VENDEDOR_URL = 'http://localhost:5003'
RECOMANADOR_URL = 'http://localhost:5010'
AGENTE_VALORACIONES_URL = 'http://localhost:5005'


# Definir el namespace
ns = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

archivo_base_datos_usuarios = "../data/usuaris.rdf"

USUARIO_REGISTRADO = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        correo = request.form['correo']
        direccion = request.form['direccion']

        # Crear un JSON con los datos del usuario
        USUARIO_REGISTRADO['nombre'] = nombre
        USUARIO_REGISTRADO['correo'] = correo
        USUARIO_REGISTRADO['direccion'] = direccion

        registrarUsuarioBD(nombre, correo, direccion)

        return """
            <h1>¡Cliente registrado correctamente!</h1>
            <form action="/buscar" method="get">
                <button type="submit">Anar pagina principal</button>
            </form>
            """
    else: 
        html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Filtrar Productes</title>
            </head>
            <body>
                <h1>Registro de Cliente</h1>
                <form method="post">
                    <label for="nombre">Nombre:</label>
                    <input type="text" id="nombre" name="nombre" required><br><br>

                    <label for="correo">Correo electrónico:</label>
                    <input type="email" id="correo" name="correo" required><br><br>

                    <label for="direccion">Dirección:</label>
                    <input type="text" id="direccion" name="direccion" required><br><br>

                    <input type="submit" value="Registrar">
                </form>
            </body>
            </html>
            """
        return html


# Función para leer la base de datos RDF
def leer_DB(ruta_archivo):
    base_datos = Graph()
    try:
        base_datos.parse(ruta_archivo, format="xml")
    except Exception as e:
        print("Error:", e)
    return base_datos

# Función para añadir un usuario a la base de datos RDF
def registrarUsuarioBD(nombre, correo, direccion):
    base_datos = leer_DB(archivo_base_datos_usuarios)

    usuario_uri = ns["Usuario_" + str(uuid.uuid4())]  # Generar URI única para el usuario
    base_datos.add((usuario_uri, RDF.type, ns.Usuario))
    base_datos.add((usuario_uri, ns.Nombre, Literal(nombre)))
    base_datos.add((usuario_uri, ns.Correo, Literal(correo)))
    base_datos.add((usuario_uri, ns.Direccion, Literal(direccion)))

    base_datos.serialize(destination=archivo_base_datos_usuarios, format="xml")


@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        nom = request.form['nom']
        preu_min = request.form['preu_min']
        preu_max = request.form['preu_max']
        categoria = request.form['categoria']
        num_valoracions_min = request.form['num_valoracions_min']
        estrelles_min = request.form['estrelles_min']

        # Crear un JSON con los datos
        filtro_json = {
            "nom": nom,
            "preu_min": preu_min,
            "preu_max": preu_max,
            "categoria": categoria,
            "num_valoracions_min": num_valoracions_min,
            "estrelles_min": estrelles_min
        }
        try:
            response = requests.post(AGENTE_URL, json=filtro_json)
            print(f"Código de estado de la respuesta: {response.status_code}")
            if response.status_code == 200:
                productosFiltrados = response.json()

                if productosFiltrados:
                    return render_template('productesFiltratsClient.html', productos=productosFiltrados)
                else:
                    print("No se encontraron productos.")
                    return "No se encontraron productos. <br><a href='/buscar'>Volver</a>"

            else:
                mensaje = "Productos no trobats." if response.status_code == 404 else "Error en el envío de los filtros."
                return f"""{mensaje}<br>
                <a href="/buscar">Tornar</a>
                """
        except Exception as e:
            # Manejo de errores
            return f"Ocurrió un error: {e}", 500

    else:
        html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Filtrar Productes</title>
            </head>
            <body>
                <h1>Filtrar Productes</h1>
                <form method="post">
                    <label for="nom">Nom:</label>
                    <input type="text" id="nom" name="nom"><br><br>
                    
                    <label for="preu_min">Precio Mínimo:</label>
                    <input type="number" step="1" id="preu_min" name="preu_min"><br><br>

                    <label for="preu_max">Precio Máximo:</label>
                    <input type="number" step="1" id="preu_max" name="preu_max"><br><br>

                    <label for="categoria">Categoría:</label>
                    <input type="text" id="categoria" name="categoria"><br><br>

                    <label for="num_valoracions_min">Número de Valoraciones Mínimo:</label>
                    <input type="number" step="1" id="num_valoracions_min" name="num_valoracions_min"><br><br>

                    <label for="estrelles_min">Estrellas Mínimas:</label>
                    <input type="number" id="estrelles_min" name="estrelles_min" min="1" max="5"><br><br>

                    <input type="submit" value="Buscar productos">
                    <p><a href="/cart">Anar carrito compra</a></p>
                </form>
                <form action="/valorar" method="post">
                    <p><a href="/valorar"><button>Fer Valoracio</button></a></p>
                </form>
                <form action="/mirarFactura" method="post">
                    <p><a href="/mirarFactura"><button>Veure factures</button></a></p>
                </form>
            </body>
            </html>
            """
        return html


@app.route('/detalls_producte', methods=['POST'])
def detalls_producte():
    try:
        prod = json.loads(request.form['producto'])
        return render_template('detalls_producte.html', producto=prod)
    except Exception as e:
        return f"Error: {e}"


@app.route('/seleccionar_producto', methods=['POST'])
def seleccionar_producto():
    try:
        prod1 = json.loads(request.form['producto'])
        print("Producto seleccionado (JSON):", prod1)
        otra_response = requests.post(AGENTE_PRODUCTE_URL, json=prod1)

        if otra_response.status_code == 200:
            print("El primer producto se ha enviado correctamente a otra URL.")
            carritoCompra.append(prod1)
            global precioTotal
            precioTotal += prod1['precio']
            return render_template('carritoCompra.html', carritoCompra=carritoCompra, precioTotal=precioTotal)
        else:
            print("Error al enviar el primer producto a otra URL.")
            return "Error al enviar el primer producto a otra URL."
    except Exception as e:
        print(f"Error al enviar el primer producto a otra URL: {e}")
        return f"Error al enviar el primer producto a otra URL: {e}"


@app.route('/cart')
def view_cart():
    return render_template('carritoCompra.html', carritoCompra=carritoCompra, precioTotal=precioTotal)


@app.route('/comprar', methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        direccion = request.form['direccion']
        if not carritoCompra:
            return """
            El carrito está vacío. Añade productos antes de proceder a la compra.<br>
            <a href="/buscar">Volver a la página principal</a>
            """
        try:
            datosCompra = {
                "carrito": carritoCompra,
                "usuario_id": USUARIO_REGISTRADO.nombre,
                "direccion": USUARIO_REGISTRADO.direccion
            }
            response = requests.post(
                VENDEDOR_URL + '/ProcesarCompra', json=datosCompra)
            if response.status_code == 200:
                carritoCompra.clear()
                global precioTotal
                precioTotal = 0
                return "Compra realizada con éxito.<br><a href='/buscar'>Volver a la página principal</a>"
            else:
                return f"Error al procesar la compra: {response.text}<br><a href='/buscar'>Volver a la página principal</a>"
        except Exception as e:
            return f"Error al enviar la información al vendedor: {e}<br><a href='/buscar'>Volver a la página principal</a>"
    else:
        return """
        <form method="post">
            <label for="direccion">Dirección de envío:</label><br>
            <input type="text" id="direccion" name="direccion" required><br><br>
            <input type="submit" value="Comprar">
        </form>
        <br><a href="/buscar">Volver a la página principal</a>
        """


@app.route('/RebreRecomanacio', methods=['POST'])
def rebre_recomanacio():
    producto_info = request.get_json()
    print(f"Producto recomendado recibido: {producto_info}")

    # Renderizar la plantilla HTML con la información del producto recomendado
    return render_template('recomendacion.html', producto=producto_info)


@app.route('/valorar', methods=['POST'])
def valorar():
    return render_template('valorar_producto.html')


@app.route('/TocaValorar', methods=['POST'])
def TocaValorar():
    print("TOCA FER VALORACIO")
    return "TOCA FER VALORACIO ENVIAT"

@app.route('/mirarFactura', methods=['POST'])
def mirarFactura():
    return render_template('factura.html', carrito=carritoGeneral, direccion=direccioGeneral, preuTotal=preuGeneral)

@app.route('/posarFactura', methods=['POST'])
def posarFactura():
    data = request.get_json()
    global carritoGeneral, direccioGeneral, preuGeneral
    carritoGeneral = data['carrito']
    direccioGeneral = data['direccion']
    preuGeneral = data['totalPreu']
    print("NOVA FACTURA A VEURE")
    return "FACTURA MOSTRADA CORRECTAMENT"


@app.route('/submit_valoracion', methods=['POST'])
def submit_valoracion():
    if request.method == 'POST':
        valoracion = request.form['valoracion']
        comentario = request.form['comentario']

        # Crear un JSON con los datos de la valoración
        data = {
            "valoracion": valoracion,
            "comentario": comentario
        }

        # Enviar los datos al agente encargado de las valoraciones
        response = requests.post(
            AGENTE_VALORACIONES_URL + '/guardar_valoracion', json=data)

        if response.status_code == 200:
            # Si la solicitud fue exitosa, devolver un mensaje de éxito
            return "Valoración enviada correctamente al agente encargado de las valoraciones"
        else:
            # Si hubo un error en la solicitud, devolver un mensaje de error
            return "Error al enviar la valoración al agente encargado de las valoraciones"
    else:
        # Si la solicitud no es POST, devolver un mensaje de error
        return "Error: La solicitud debe ser POST", 400


if __name__ == "__main__":
    app.run(port=5007)
