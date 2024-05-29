#!/bin/bash
# Start Directory Service
cd agents
python3 directory.py &

# Start Agent 1

python3 agent1.py &

# Start Agent 2

python3 agent2.py &

# Start Agent Seller

python3 SellerAgent.py &

# Wait to ensure all services are up
sleep 3

# Display the URLs for access
echo "Directory Service running at http://localhost:5000"
echo "Agent 1 running at http://localhost:5001"
echo "Agent 2 running at http://localhost:5002"
echo "Agent 3 running at http://localhost:5003"

