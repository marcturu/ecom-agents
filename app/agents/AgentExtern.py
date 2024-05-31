import random
import sys
import uuid
from flask import Flask, render_template, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, FOAF, XSD

# Definir los namespaces necesarios
ECSDI = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/PracticaECSDI#")
DSO = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/DSO#")
ACL = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/ACL#")
agn = Namespace("http://www.semanticweb.org/hp/ontologies/2024/4/agn#")

app = Flask(__name__, template_folder='templates')

@app.route('/registrarProducto', methods=['GET', 'POST'])
def browser_registrarProducto():
    """
    Permite la comunicación con el agente vía un navegador
    mediante un formulario
    """
    if request.method == 'GET':
        return render_template('registerProduct.html')
    else:
        marca = request.form['marca']
        nom = request.form['nom']
        model = request.form['model']
        preu = request.form['preu']
        peso = request.form['peso']
        vendido = 0

        # Content of the message
        content = ECSDI['Registra_productes_' + str(get_count())]

        # Graph creation
        gr = Graph()
        gr.add((content, RDF.type, ECSDI.Registra_productes))

        # Añadir nuevo producto externo al grafo
        subjectProd = ECSDI['Producto_externo_' + str(uuid.uuid4())]

        gr.add((subjectProd, RDF.type, ECSDI.Producto_externo))
        gr.add((subjectProd, ECSDI.Nombre, Literal(nom, datatype=XSD.string)))
        gr.add((subjectProd, ECSDI.Marca, Literal(marca, datatype=XSD.string)))
        gr.add((subjectProd, ECSDI.Modelo, Literal(model, datatype=XSD.string)))
        gr.add((subjectProd, ECSDI.Precio, Literal(preu, datatype=XSD.float)))
        gr.add((subjectProd, ECSDI.Peso, Literal(peso, datatype=XSD.float)))
        gr.add((subjectProd, ECSDI.Vendido, Literal(vendido)))

        gr.add((content, ECSDI.producto, subjectProd))

        productsag = getagent_info(agn.ProductsAgent, DirectoryAgent, AgentExternal, get_count())

        send_message(
            build_message(gr, perf=ACL.request, sender=AgentExternal.uri, receiver=productsag.uri,
                          msgcnt=get_count(),
                          content=content), productsag.address)

        res = {'marca': marca, 'nom': nom, 'model': model, 'preu': preu, 'peso': peso}

        return render_template('endRegister.html', product=res)

def getagent_info(type, directoryagent, sender, msgcnt):
    gmess = Graph()
    gmess.bind('foaf', FOAF)
    gmess.bind('dso', DSO)
    ask_obj = agn[sender.name + '-Search']

    gmess.add((ask_obj, RDF.type, DSO.Search))
    gmess.add((ask_obj, DSO.AgentType, type))
    gr = send_message(build_message(gmess, perf=ACL.request, sender=sender.uri, receiver=directoryagent.uri, msgcnt=msgcnt, content=ask_obj), directoryagent.address)
    
    dic = get_message_properties(gr)
    content = dic.get('content')

    if content is None:
        raise ValueError("Content not found in the response graph")

    address = gr.value(subject=content, predicate=DSO.Address)
    url = gr.value(subject=content, predicate=DSO.Uri)
    name = gr.value(subject=content, predicate=FOAF.name)

    # Añade verificaciones
    if address is None:
        raise ValueError("Address not found in the response graph")
    if url is None:
        raise ValueError("URL not found in the response graph")
    if name is None:
        raise ValueError("Name not found in the response graph")

    return Agent(name, url, address, None)

def registeragent(origin_agent, directory_agent, type, msgcnt):
    gmess = Graph()
    gmess.bind('foaf', FOAF)
    gmess.bind('dso', DSO)
    reg_obj = agn[origin_agent.name + '-Register']
    gmess.add((reg_obj, RDF.type, DSO.Register))
    gmess.add((reg_obj, DSO.Uri, origin_agent.uri))
    gmess.add((reg_obj, FOAF.name, Literal(origin_agent.name)))
    gmess.add((reg_obj, DSO.Address, Literal(origin_agent.address)))
    gmess.add((reg_obj, DSO.AgentType, type))
    gr = send_message(
        build_message(gmess, perf=ACL.request,
                      sender=origin_agent.uri,
                      receiver=directory_agent.uri,
                      content=reg_obj,
                      msgcnt=msgcnt),
        directory_agent.address)

# Funciones adicionales necesarias

def get_count():
    return random.randint(1, 1000)

def send_message(message, address):
    pass

def build_message(graph, perf, sender, receiver, msgcnt, content):
    return graph

def get_message_properties(graph):
    # Ejemplo de implementación
    return {'content': next(graph.subjects(predicate=RDF.type, object=DSO.Response), None)}

class Agent:
    def __init__(self, name, uri, address, agentType):
        self.name = name
        self.uri = uri
        self.address = address
        self.agentType = agentType

AgentExternal = Agent("AgentExternal", "http://example.org/AgentExternal", "http://example.org/address", None)
DirectoryAgent = Agent("DirectoryAgent", "http://example.org/DirectoryAgent", "http://example.org/address", None)

if __name__ == "__main__":
    app.run(port=5000)
    