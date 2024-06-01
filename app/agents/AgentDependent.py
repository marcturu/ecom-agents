from flask import Flask, request, render_template, redirect, url_for, jsonify
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests
import json

app = Flask(__name__)

base_datos_productos = "../data/productes.rdf"
base_datos_productesCercats = "../data/productesCercats.rdf"
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

def leer_DB(ruta_archivo):
    base_datos = Graph()

    try:
        base_datos.parse(ruta_archivo, format="xml")
        print("Productos en la base de datos RDF:")

        # Iterar sobre todos los sujetos que son de tipo 'Producte'
        for producto in base_datos.subjects(RDF.type, ECSDI.Producte):
            nombre = base_datos.value(producto, ECSDI.Nom)
            precio = base_datos.value(producto, ECSDI.Preu)
            categoria = base_datos.value(producto, ECSDI.Categoria)
            descripcion = base_datos.value(producto, ECSDI.Descripcio)
            num_valoraciones = base_datos.value(producto, ECSDI.NumValoracions)
            estrellas_mitges = base_datos.value(producto, ECSDI.EstrellesMitges)

            print(f" Producto: {nombre}")
            print(f"  Precio: {precio}")
            print(f"  Categoría: {categoria}")
            print(f"  Descripción: {descripcion}")
            print(f"  Número de Valoraciones: {num_valoraciones}")
            print(f"  Estrellas Medias: {estrellas_mitges}")
            print("---")

    except Exception as e:
        print("Error:", e)

    return base_datos

@app.route('/', methods=['GET', 'POST'])
def home():
    return "<h1>Bienvenido al agente dependiente</h1>"

@app.route("/FiltrarProducte", methods=['GET', 'POST'])
def cerca():

    #x = request.json()
    # x.get("nom", "")

    # Coger filtros que pasa el usuario
    '''if request.method == 'POST':
        nom = request.form['nom']
        preu = request.form['preu']
        categoria = request.form['categoria']
        numValoracions = request.form['numValoracions']
        estrellesMitges = request.form['estrellesMitges']
    '''

    data = request.get_json()
    print(f"Datos recibidos: {data}")
    #return jsonify({"status": "success", "data": data}), 200

    # Definir los filtros
    filtros = {
        'nom': data.get('nom', ''),
        'preu': data.get('preu', ''),
        'categoria': data.get('categoria', ''),
        'numValoracions': data.get('numValoracions', ''),
        'estrellesMitges': data.get('estrellesMitges', '')
    }

    base_datos = leer_DB(base_datos_productos)

    # Filtrar productos
    productos_filtrados = Graph()

    for producto in base_datos.subjects(RDF.type, ECSDI.Producte):
        nombre = base_datos.value(producto, ECSDI.Nom)
        precio = base_datos.value(producto, ECSDI.Preu)
        categoria_producto = base_datos.value(producto, ECSDI.Categoria)
        descripcion = base_datos.value(producto, ECSDI.Descripcio)
        num_valoraciones = base_datos.value(producto, ECSDI.NumValoracions)
        estrellas_mitges = base_datos.value(producto, ECSDI.EstrellesMitges)

        # Verificar si el producto cumple con todos los filtros
        if ((not filtros['nom'] or filtros['nom'].lower() in str(nombre).lower()) and
                (not filtros['preu'] or float(precio) <= float(filtros['preu'])) and
                (not filtros['categoria'] or filtros['categoria'].lower() in str(categoria_producto).lower()) and
                (not filtros['numValoracions'] or (num_valoraciones and int(num_valoraciones) >= int(filtros['numValoracions']))) and
                (not filtros['estrellesMitges'] or filtros['estrellesMitges'] in str(estrellas_mitges))):
            '''
            # Agregar el producto a los productos filtrados
            productos_filtrados.add((producto, RDF.type, ECSDI.Producte))
            if nombre:
                productos_filtrados.add((producto, ECSDI.Nom, nombre))
            if precio:
                productos_filtrados.add((producto, ECSDI.Preu, precio))
            if categoria_producto:
                productos_filtrados.add((producto, ECSDI.Categoria, categoria_producto))
            if descripcion:
                productos_filtrados.add((producto, ECSDI.Descripcio, descripcion))
            if num_valoraciones:
                productos_filtrados.add((producto, ECSDI.NumValoracions, num_valoraciones))
            if estrellas_mitges:
                productos_filtrados.add((producto, ECSDI.EstrellesMitges, estrellas_mitges)) 

    return productos_filtrados.serialize(format='xml')'''

            # Crear un objeto JSON para el producto filtrado y agregarlo a la lista
            producto_filtrado = {
                'nombre': nombre if nombre else '',
                'precio': float(precio) if precio else 0.0,
                'categoria': categoria_producto if categoria_producto else '',
                'descripcion': descripcion if descripcion else '',
                'num_valoraciones': int(num_valoraciones) if num_valoraciones else 0,
                'estrellas_mitges': int(estrellas_mitges) if estrellas_mitges else 0
            }
            productos_filtrados_list.append(producto_filtrado)

    # Devolver la lista de productos filtrados como respuesta JSON
    try:
        response = requests.post('http://localhost:5006/', json=productos_filtrados_list)
        print(f"Código de estado de la respuesta: {response.status_code}")
        if response.status_code == 200:
            return """Productes filtrats enviats correctament <br>
                    <a href="/">Tornar</a>
                    """
        else:
            return """Error en l'enviament dels productes filtrats <br>
                    <a href="/">Tornar</a>
                    """
    except Exception as e:
        return f"""Error en l'enviament dels productes filtrats: {e} <br>
                <a href="/">Tornar</a>
                """

    '''else:
        return "Método no soportado", 405 '''


@app.route("/MostrarProducte", methods=['GET', 'POST'])
def mostrar():
    # Obtener el cuerpo del mensaje JSON de la solicitud
    #data = request.json
    producto = {
        'nom': 'Moto',
        'preu': 1000,
        'categoria': 'Automobils',
        'descripcio': 'Moto 125cc',
        'numValoracions': 4,
        'estrellesMitges': 4
    }

    data = {'producto_seleccionado': producto['nom'], 'nombre_usuario': "Marc"}

    # Verificar si se proporcionó el nombre del producto seleccionado y el nombre de usuario en la solicitud
    if 'producto_seleccionado' in data and 'nombre_usuario' in data:
        producto_seleccionado = data['producto_seleccionado']
        nombre_usuario = data['nombre_usuario']

        # Guardar el nombre del producto y el nombre del usuario en la base de datos
        if producto_seleccionado and nombre_usuario:
            guardar_producto_cercat(producto_seleccionado, nombre_usuario)
            return jsonify(producto)
            #return jsonify({"message": f"El producto '{producto_seleccionado}' ha sido guardado en la base de datos por el usuario '{nombre_usuario}'."}), 200
    else:
        return jsonify({"error": "Debe proporcionar el nombre del producto seleccionado y el nombre de usuario en el cuerpo del mensaje."}), 400

def guardar_producto_cercat(nombre_producto, nombre_usuario):
    # Cargar la base de datos de productos cercados si no ha sido cargada previamente
    if not hasattr(guardar_producto_cercat, 'base_datos_productes_cercats'):
        guardar_producto_cercat.base_datos_productes_cercats = leer_DB(base_datos_productesCercats)

    # Crear una nueva URI para el producto
    producto_uri = ECSDI[f"Producte_{nombre_producto.replace(' ', '')}"]

    # Agregar tripleta a la base de datos
    guardar_producto_cercat.base_datos_productes_cercats.add((producto_uri, ECSDI.ProducteCercat, Literal(nombre_producto)))
    guardar_producto_cercat.base_datos_productes_cercats.add((producto_uri, ECSDI.Usuario, Literal(nombre_usuario)))

    # Guardar la base de datos en un archivo
    guardar_producto_cercat.base_datos_productes_cercats.serialize(destination="../data/productesCercats.rdf", format="xml")

    return

#Regsitsrar a BD productesCercats

def register_with_directory():
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': 'AgentDependent',
        'location': 'http://localhost:5006'
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print('Registered successfully with the directory')
    else:
        print('Failed to register with the directory')

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5006)