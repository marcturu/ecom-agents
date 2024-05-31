from flask import Flask, request, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests


app = Flask(__name__)

archivo_base_datos = "../data/productes.rdf"

# Definir el namespace
ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return """
            IMPLEMENTAR ALGO AQUI
        """

    else:
        html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Añadir Producto Externo</title>
            </head>
            <body>
                <h1>Añadir Nuevo Producto Externo</h1>
                <form method="post">
                    <label for="nom">Nom:</label>
                    <input type="text" id="nom" name="nom" required><br><br>

                    <label for="preu">Preu:</label>
                    <input type="number" step="1" id="preu" name="preu" required><br><br>

                    <label for="categoria">Categoria:</label>
                    <input type="text" id="categoria" name="categoria" required><br><br>

                    <label for="descripcio">Descripcio:</label>
                    <input type="text" id="descripcio" name="descripcio" required><br><br>

                    <label for="numValoracions">Num. Valoracions:</label>
                    <input type="number" step="1" id="numValoracions" name="numValoracions" required><br><br>

                    <label for="estrellesMitges">Estrelles mitges (1-5):</label>
                    <input type="number" id="estrellesMitges" name="estrellesMitges" min="1" max="5" required><br><br>

                    <input type="submit" value="Añadir Producto">
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
