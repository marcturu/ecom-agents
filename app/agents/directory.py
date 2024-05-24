from flask import Flask, jsonify

app = Flask(__name__)

# Directory of agents
agents = {
    'Agent1': 'http://localhost:5001',
    'Agent2': 'http://localhost:5002'
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


if __name__ == "__main__":
    app.run(port=5000)
