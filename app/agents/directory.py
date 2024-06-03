from flask import Flask, render_template, jsonify, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF

app = Flask(__name__)

# Directory of agents
agents = {
    'AgentVenedor': 'http://localhost:5003',
    'AgentExtern': 'http://localhost:5004',
    'AgentValoracions': 'http://localhost:5005',
    'AgentDependent': 'http://localhost:5006',
    'Client': 'http://localhost:5007',
    'AgentRecomanador': 'http://localhost:5010'
}

@app.route('/')
def home():
    return "Directory Service"


@app.route('/agents')
def list_agents():
    return jsonify(agents)


@app.route('/agents/<name>')
def get_agent(name):
    location = agents.get(name)
    if location:
        return jsonify({'name': name, 'location': location})
    else:
        return "Agent not found", 404


@app.route('/register', methods=['POST'])
def register_agent():
    agent_data = request.get_json()
    agents[agent_data['name']] = agent_data['location']
    return jsonify(agents), 201


if __name__ == "__main__":
    app.run(port=5000)
  