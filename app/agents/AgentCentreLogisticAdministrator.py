import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

logistic_centers = [
    'http://localhost:5012',  # Example logistic center URL
    # Add more logistic center URLs as needed
]


@app.route('/')
def home():
    return "<h1>Bienvenido al Administrador del Centro Logístico</h1>"


@app.route('/ProcesarPedido', methods=['POST'])
def procesar_pedido():
    try:
        data = request.get_json()
        carrito = data['carrito']
        direccion = data['direccion']
        print(f"Pedido recibido: {carrito}")
        print(f"Dirección de entrega: {direccion}")

        for producto in carrito:
            nombre_producto = producto['nombre']
            if consultar_centros_logisticos(nombre_producto):
                print(f"El producto {
                      nombre_producto} está disponible en un centro logístico.")
                solicitar_envio_producto(nombre_producto, direccion)
            else:
                print(f"El producto {
                      nombre_producto} NO está disponible en ningún centro logístico.")

        return jsonify({"message": "Pedido procesado con éxito"}), 200
    except Exception as e:
        print(f"Error en el procesamiento del pedido: {e}")
        return jsonify({"error": str(e)}), 500


def consultar_centros_logisticos(nombre_producto):
    for lc_url in logistic_centers:
        response = requests.post(
            f"{lc_url}/VerificarProducto", json={"nombre_producto": nombre_producto})
        if response.status_code == 200:
            resultado = response.json()
            if resultado['disponible']:
                return True
    return False


def solicitar_envio_producto(nombre_producto, direccion):
    for lc_url in logistic_centers:
        response = requests.post(
            f"{lc_url}/PrepararEnvio", json={"nombre_producto": nombre_producto, "direccion": direccion})
        if response.status_code == 200:
            print(f"Solicitud de envío para {
                  nombre_producto} enviada al centro logístico.")
            return True
    return False


def register_with_directory(agent_name, agent_location):
    directory_url = 'http://localhost:5000/register'
    agent_info = {
        'name': agent_name,
        'location': agent_location
    }
    response = requests.post(directory_url, json=agent_info)
    if response.status_code == 201:
        print(f'{agent_name} registered successfully with the directory')
    else:
        print(f'Failed to register {agent_name} with the directory')


if __name__ == "__main__":
    register_with_directory(
        'LogisticCenterAdministratorAgent', 'http://localhost:5013')
    app.run(port=5013)
