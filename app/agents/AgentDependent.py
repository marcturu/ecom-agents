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
      

if __name__ == "__main__":
    register_with_directory()
    app.run(port=5006)
