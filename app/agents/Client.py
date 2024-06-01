from flask import Flask, request, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests

app = Flask(__name__)


AGENTE_URL = 'http://localhost:5006/'

# Definir el namespace
ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
  

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
                productos = response.json()
                # primer_producto = productos[0] if productos else None
                # response = requests.post(AGENTE_URL, json=primer_producto)
                return render_template('productesFiltratsClient.html', productos=productos)
            
                # return """Filtres registrats correctament <br>
                #     <a href="/">Afegir nous filtres</a>
                #     """
            else:
                return """Error en l'enviament dels filtres <br>
                    <a href="/">Tornar</a>
                    """
        except Exception as e:
            return f"""Error en l'enviament dels filtres: {e} <br>
                <a href="/">Tornar</a>
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

                    <input type="submit" value="Filtrar">
                </form>
            </body>
            </html>
            """
        return html



if __name__ == "__main__":
    app.run(port=5007)
