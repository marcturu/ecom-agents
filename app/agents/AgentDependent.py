from flask import Flask, request, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import requests

app = Flask(__name__)

archivo_base_datos = "../data/productes.rdf"

ns = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
  

@app.route('/')
def home():
    return "Hello from Agent Dependent"

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

# IDEES DE COSES A FER/MOSTRAR DE UN ALTRE ANY:
# Buscar sin filtro -> Retrona todos los productos de la base de datos.
# Buscar por nombre = Cable -> Retorna un producto llamado Cable.
# Buscar por precio máximo = 100 -> Retorna los poroductos con un precio inferior a 100.
# Buscar por precio mínimo = 100 -> Retorn a los productos con un precio superior a 100.
# Bucar por precio máximo = 100 y mínimo = 100 y nombre = Cable -> Retorna el producto Cable 

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5006)
