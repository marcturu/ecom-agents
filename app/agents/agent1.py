from flask import Flask, request, render_template, redirect, url_for
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid

app = Flask(__name__, template_folder='templates')

# Definir el namespace
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")

@app.route('/')
def home():
    return "Hello from Agent 1"

if __name__ == "__main__":
    app.run(port=5001)