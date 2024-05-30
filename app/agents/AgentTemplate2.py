# -*- coding: utf-8 -*-
"""
Esqueleto de otro agente usando los servicios web de Flask

/comm es la entrada para la recepcion de mensajes del agente
/Stop es la entrada que para el agente

Tiene una funcion AgentBehavior2 que se lanza como un thread concurrente

Asume que el agente de registro esta en el puerto 5000

@author: tu_nombre
"""

from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph
from flask import Flask

from utils.FlaskServer import shutdown_server
from utils.Agent import Agent

__author__ = 'tu_nombre'

# Configuration stuff
hostname = socket.gethostname()
port = 9020  # Cambiar al puerto que desees para este agente

agn = Namespace("http://www.agentes.org#")

# Contador de mensajes
mss_cnt = 0

# Datos del Agente

AgenteTemplate2 = Agent('AgentTemplate2',
                        agn.AgentTemplate2,
                        'http://%s:%d/comm' % (hostname, port),
                        'http://%s:%d/Stop' % (hostname, port))

# Directory agent address
DirectoryAgent = 'http://localhost:5000/register'  # Cambiar si el servicio de registro no está en localhost:5000

# Global triplestore graph
dsgraph = Graph()

cola2 = Queue()

# Flask stuff
app = Flask(__name__)


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt
    pass


@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente

    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


def tidyup():
    """
    Acciones previas a parar el agente

    """
    pass


def agentbehavior2(cola):
    """
    Un comportamiento del agente

    :return:
    """
    pass


if __name__ == '__main__':
    # Ponemos en marcha los behaviors
    ab2 = Process(target=agentbehavior2, args=(cola2,))
    ab2.start()

    # Ponemos en marcha el servidor
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    ab2.join()
    print('The End')
