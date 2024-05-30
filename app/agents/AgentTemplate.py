# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Esqueleto de agente usando los servicios web de Flask

/comm es la entrada para la recepcion de mensajes del agente
/Stop es la entrada que para el agente

Tiene una funcion AgentBehavior1 que se lanza como un thread concurrente

Asume que el agente de registro esta en el puerto 9000

@author: javier
"""


from multiprocessing import Process, Queue
import socket
import requests

from rdflib import Namespace, Graph
from flask import Flask, request

from utils.FlaskServer import shutdown_server
from utils.Agent import Agent

__author__ = 'javier'

# Configuration stuff
hostname = socket.gethostname()
port = 9010

agn = Namespace("http://www.agentes.org#")

# Contador de mensajes
mss_cnt = 0

# Datos del Agente

AgentePersonal = Agent('AgenteSimple',
                       agn.AgenteSimple,
                       'http://%s:%d/comm' % (hostname, port),
                       'http://%s:%d/Stop' % (hostname, port))

# Directory agent address
DirectoryAgent = Agent('DirectoryAgent',
                       agn.Directory,
                       'http://%s:9000/Register' % hostname,
                       'http://%s:9000/Stop' % hostname)

# Global triplestore graph
dsgraph = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__)


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


def agentbehavior1(cola):
    """
    Un comportamiento del agente

    :return:
    """
    pass

# Función para enviar un mensaje a otro agente
def enviar_mensaje(destino, mensaje):
    print("Enviando mensaje a", destino, ":", mensaje)

    url_destino = "http://localhost:{}/comm".format(destino)
    response = requests.post(url_destino, json=mensaje)
    # Procesar la respuesta si es necesario
    if response.status_code == 200:
        print("Mensaje enviado con éxito a {}".format(destino))
    else:
        print("Error al enviar mensaje a {}".format(destino))

# Ejemplo de cómo enviar un mensaje desde AgentTemplate.py a AgentTemplate2.py
mensaje_para_agent2 = {"contenido": "Hola, soy AgentTemplate1"}
enviar_mensaje(9020, mensaje_para_agent2)


@app.route("/comm", methods=['POST'])
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt

    # Obtener el contenido del mensaje recibido
    mensaje_recibido = request.get_json()
    print("Mensaje recibido:", mensaje_recibido)

    # Lógica para procesar el mensaje

    return "OK"  # O la respuesta que desees enviar al agente remitente


if __name__ == "__main__":
    app.run(port=9000)



# if __name__ == '__main__':
#     # Ponemos en marcha los behaviors
#     ab1 = Process(target=agentbehavior1, args=(cola1,))
#     ab1.start()

#     # Ponemos en marcha el servidor
#     app.run(host=hostname, port=port)

#     # Esperamos a que acaben los behaviors
#     ab1.join()
#     print('The End')
