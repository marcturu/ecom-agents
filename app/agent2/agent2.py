from flask import Flask, jsonify
from rdflib import Graph

app = Flask(__name__)


@app.route('/')
def home():
    return "Hello from Agent 2"


if __name__ == "__main__":
    app.run(port=5002)
