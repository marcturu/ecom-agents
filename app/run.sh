#!/bin/bash
# Start Directory Service
cd agents
python3 directory.py &

# Start Agent 1

python3 agent1.py &

# Start Agent 2

python3 agent2.py &

# Start Agent Venedor

python3 AgentVenedor.py &

# Start Agent Extern

python3 AgentExtern.py &

# Start Agent Valoracions

python3 AgentValoracions.py &

# Start Agent Dependent

python3 AgentDependent.py &

# Start Client

python3 Client.py &

# Start Agent Tresorer

python3 AgentTresorer.py &

# Start Agent Recomanador

python3 AgentRecomanador.py &

# Start Extern Productes

python3 ExternProductes.py &

# Wait to ensure all services are up
sleep 3

# Display the URLs for access
echo "Directory Service running at http://localhost:5000"
echo "Agent 1 running at http://localhost:5001"
echo "Agent 2 running at http://localhost:5002"
echo "Agent 3 running at http://localhost:5003"
echo "Agent 4 running at http://localhost:5004"
echo "Agent 5 running at http://localhost:5005"
echo "Agent 6 running at http://localhost:5006"
echo "Agent 7 running at http://localhost:5007"
echo "Agent 8 running at http://localhost:5008"
echo "Agent 9 running at http://localhost:5010"
echo "Agent 10 running at http://localhost:5011"



