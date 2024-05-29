from flask import Flask, request, jsonify
from rdflib import Graph

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Agent 1"

@app.route('/receive_message', methods=['POST'])
def receive_message():
    serialized_message = request.data

    received_graph = Graph()
    received_graph.parse(data=serialized_message)

    return "Message received successfully by Agent 1"

if __name__ == "__main__":
    app.run(port=5001)
