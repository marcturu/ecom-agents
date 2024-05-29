from flask import Flask, jsonify, request

app = Flask(__name__)

# Directory of agents
agents = {
    'Agent1': 'http://localhost:5001',
    'Agent2': 'http://localhost:5002',
    'SellerAgent': 'http://localhost:5003'
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