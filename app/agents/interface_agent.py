import os
import signal
import socket

import requests
from flask import Flask, jsonify, render_template, request

# Flask app setup
hostname = socket.gethostname()
port = 5003

# Directory agent address
directory_address_hostname = socket.gethostname()
directory_address_port = 5000
directory_agent_url = f'http://{directory_address_hostname}:{
    directory_address_port}/GetAgents'

# Flask app
app = Flask(__name__, template_folder='templates')


@app.route("/Stop")
def stop():
    try:
        shutdown_server()
    except Exception as e:
        print(f"Error stopping server: {e}")
        print('Using Alternative stopping method...')
        os.kill(os.getpid(), signal.SIGINT)
    return "InterfaceAgent stopping..."


def get_agent_dir(agent):
    response = requests.get(directory_agent_url)
    response_body = response.json()
    agent_address = response_body.get(agent)
    return agent_address


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/comm', methods=['GET'])
def communicate():
    url = get_agent_dir('Agent1')
    data = {
        'type': 'request',
        'performative': 'infoProd',
        'product': 'laptop',
        'receiver': 'Agent1'
    }
    requests.post(url, json=data)

    return "OK"


@app.route('/GetAgents', methods=['GET'])
def get_agents():
    response = requests.get(directory_agent_url)
    return jsonify(response.json())


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    else:
        print("werkzeug.server.shutdown is not available. Using os.kill to terminate the process.")
        os.kill(os.getpid(), signal.SIGINT)


if __name__ == "__main__":
    app.run(host=hostname, port=port)
