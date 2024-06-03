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

AGENTE_URL = 'http://localhost:5006/FiltrarProducte'
AGENTE_PRODUCTE_URL = 'http://localhost:5006/MostrarProducte'
VENDEDOR_URL = 'http://localhost:5003'
RECOMANADOR_URL = 'http://localhost:5010'
AGENTE_VALORACIONES_URL = 'http://localhost:5005'


USER_ID = "Manolo"

# Definir el namespace
ns = Namespace(
    "http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")


@app.route('/', methods=['GET', 'POST'])
def home():
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
                    return "No se encontraron productos. <br><a href='/'>Volver</a>"

            else:
                mensaje = "Productos no trobats." if response.status_code == 404 else "Error en el envío de los filtros."
                return f"""{mensaje}<br>
                <a href="/">Tornar</a>
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
            <a href="/">Volver a la página principal</a>
            """
        try:
            datosCompra = {
                "carrito": carritoCompra,
                "usuario_id": USER_ID,
                "direccion": direccion
            }
            response = requests.post(
                VENDEDOR_URL + '/ProcesarCompra', json=datosCompra)
            if response.status_code == 200:
                carritoCompra.clear()
                global precioTotal
                precioTotal = 0
                return "Compra realizada con éxito.<br><a href='/'>Volver a la página principal</a>"
            else:
                return f"Error al procesar la compra: {response.text}<br><a href='/'>Volver a la página principal</a>"
        except Exception as e:
            return f"Error al enviar la información al vendedor: {e}<br><a href='/'>Volver a la página principal</a>"
    else:
        return """
        <form method="post">
            <label for="direccion">Dirección de envío:</label><br>
            <input type="text" id="direccion" name="direccion" required><br><br>
            <input type="submit" value="Comprar">
        </form>
        <br><a href="/">Volver a la página principal</a>
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
