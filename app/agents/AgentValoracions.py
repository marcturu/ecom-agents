from flask import Flask, request, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests

app = Flask(__name__)

# archivo_base_datos = "../data/productes.rdf"

# # Definir el namespace
# ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Procesar la valoración del producto enviado por el usuario
        valoracion = request.form['valoracion']
        # Aquí puedes agregar la lógica para registrar la valoración en tu base de datos
        # por ejemplo, almacenarla en una base de datos o enviarla a través de un mensaje a otro agente

        return f"""
            Producto valorado correctamente con una puntuación de {valoracion}. <br>           
            <a href="/">Valorar otro producto</a>
        """

    else:
        html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Valorar Producto</title>
            </head>
            <body>
                <h1>Valorar Producto</h1>
                <form method="post">
                    <label for="valoracion">Valoración (1-5):</label>
                    <input type="number" id="valoracion" name="valoracion" min="1" max="5" required><br><br>
                    <input type="submit" value="Enviar Valoración">
                </form>
            </body>
            </html>
        """
        return html

def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'SellerAgent',
        'location': 'http://localhost:5005'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')
      

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5005)
