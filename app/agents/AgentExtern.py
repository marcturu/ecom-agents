from flask import Flask, request, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests


app = Flask(__name__)

archivo_base_datos = "../data/productes.rdf"

# Definir el namespace
ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
  
# Función para leer la base de datos RDF
def leer_DB(ruta_archivo):
    base_datos = Graph()
    
    try:
        base_datos.parse(ruta_archivo, format="xml")
        print("Productos en la base de datos RDF:")
        
        # Iterar sobre todos los sujetos que son de tipo 'Producte'
        for producto in base_datos.subjects(RDF.type, ns.Producte):
            nombre = base_datos.value(producto, ns.Nom)
            precio = base_datos.value(producto, ns.Preu)
            categoria = base_datos.value(producto, ns.Categoria)
            descripcion = base_datos.value(producto, ns.Descripcio)
            num_valoraciones = base_datos.value(producto, ns.NumValoracions)
            estrellas_mitges = base_datos.value(producto, ns.EstrellesMitges)

            print(f"Producto: {nombre}")
            print(f"  Precio: {precio}")
            print(f"  Categoría: {categoria}")
            print(f"  Descripción: {descripcion}")
            print(f"  Número de Valoraciones: {num_valoraciones}")
            print(f"  Estrellas Medias: {estrellas_mitges}")
            print("---")
            
    except Exception as e:
        print("Error:", e)
    return base_datos

# Función para añadir un producto a la base de datos RDF
def añadir_producto(nom, preu, categoria, descripcio, numValoracions, estrellesMitges):
    base_datos = leer_DB(archivo_base_datos)

    product_uri = ns["Producte_" + nom.replace(" ", "_")]  # Generar URI única para el producto
    base_datos.add((product_uri, RDF.type, ns.Producte))
    base_datos.add((product_uri, ns.Nom, Literal(nom)))
    base_datos.add((product_uri, ns.Preu, Literal(preu)))
    base_datos.add((product_uri, ns.Categoria, Literal(categoria)))
    base_datos.add((product_uri, ns.Descripcio, Literal(descripcio)))
    base_datos.add((product_uri, ns.NumValoracions, Literal(numValoracions)))
    base_datos.add((product_uri, ns.EstrellesMitges, Literal(estrellesMitges)))

    base_datos.serialize(destination=archivo_base_datos, format="xml")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nom = request.form['nom']
        preu = request.form['preu']
        categoria = request.form['categoria']
        descripcio = request.form['descripcio']
        numValoracions = request.form['numValoracions']
        estrellesMitges = request.form['estrellesMitges']

        añadir_producto(nom, preu, categoria, descripcio, numValoracions, estrellesMitges)

        return """
            Producto añadido correctamente a la base de datos RDF.<br>
            <a href="/">Añadir Nuevo Producto</a>
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
        'location': 'http://localhost:5004'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')
      

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5004)
