import requests
import json

class AgenteSimple:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.url_receptor = f'http://{self.hostname}:{self.port}/comm'

    def enviar_mensaje(self, mensaje):
        try:
            # Convertir el mensaje a formato JSON
            mensaje_json = json.dumps(mensaje)

            # Enviar el mensaje al agente receptor
            respuesta = requests.post(self.url_receptor, json=mensaje_json)

            # Verificar la respuesta
            if respuesta.status_code == 200:
                print("Mensaje enviado con éxito.")
            else:
                print("Error al enviar el mensaje:", respuesta.status_code)
        except Exception as e:
            print("Error al enviar el mensaje:", e)

# Crear una instancia del agente
mi_agente = AgenteSimple('localhost', 9010)

# Crear un mensaje para enviar
mensaje = {
    'tipo': 'informacion',
    'contenido': 'Hola, este es un mensaje de ejemplo.'
}

# Enviar el mensaje usando el método enviar_mensaje()
mi_agente.enviar_mensaje(mensaje)
