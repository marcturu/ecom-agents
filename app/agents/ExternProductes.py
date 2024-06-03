from flask import Flask, request, render_template, redirect, url_for
import requests

app = Flask(__name__)

AGENT_EXTERN_URL = 'http://localhost:5004'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nom = request.form['nom']
        preu = request.form['preu']
        categoria = request.form['categoria']
        descripcio = request.form['descripcio']
        numValoracions = request.form['numValoracions']
        estrellesMitges = request.form['estrellesMitges']

        # Comunicarse con el Agente Externo para guardar el producto en la base de datos
        response = requests.post(AGENT_EXTERN_URL + '/external_products', json={
            'nom': nom,
            'preu': preu,
            'categoria': categoria,
            'descripcio': descripcio,
            'numValoracions': numValoracions,
            'estrellesMitges': estrellesMitges
        })

        if response.status_code == 200:
            return """
                Producto añadido correctamente a la base de datos RDF.<br>
                <a href="/">Añadir Nuevo Producto</a>
            """
        else:
            return "Error al añadir el producto a la base de datos RDF"

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

if __name__ == "__main__":
    app.run(port=5011)
