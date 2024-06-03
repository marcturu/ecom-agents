#!/bin/bash

# Function to kill processes by port number
kill_by_port() {
    PORT=$1
    PID=$(lsof -t -i:$PORT)
    if [ ! -z "$PID" ]; then
        echo "Killing process on port $PORT with PID $PID"
        kill -9 $PID
    else
        echo "No process found on port $PORT"
    fi
}

# Kill the directory service (port 5000)
kill_by_port 5000

# Kill Agent 1 (port 5001)
kill_by_port 5001

# Kill Agent 2 (port 5002)
kill_by_port 5002

# Kill Agent Venedor (port 5003)
kill_by_port 5003

# Kill Agent Extern (port 5004)
kill_by_port 5004

# Kill Agent Valoracions (port 5005)
kill_by_port 5005

# Kill Agent Dependent (port 5006)
kill_by_port 5006

# Kill Client (port 5007)
kill_by_port 5007

# Kill Client (port 5010)
kill_by_port 5010

echo "All agents and the directory service have been terminated."
