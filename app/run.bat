@echo off

:: Start Directory Service
echo Starting Directory Service on port 5000...
start "Directory Service" cmd /c "cd agents && python directory.py"

:: Wait a bit to ensure the directory service starts
timeout /t 2 /nobreak > NUL

:: Start Agent 1
echo Starting Agent 1 on port 5001...
start "Agent 1" cmd /c "cd agents && python agent1.py"

:: Start Agent 2
echo Starting Agent 2 on port 5002...
start "Agent 2" cmd /c "cd agents && python agent2.py"

:: Start Agent Venedor
echo Starting Agent Venedor on port 5003...
start "Agent Venedor" cmd /c "cd agents && python AgentVenedor.py"

:: Start Agent Extern
echo Starting Agent Extern on port 5004...
start "Agent Extern" cmd /c "cd agents && python AgentExtern.py"

:: Start Agent Valoracions
echo Starting Agent Extern on port 5005...
start "Agent Valoracions" cmd /c "cd agents && python AgentValoracions.py"

:: Start Agent Dependent
echo Starting Agent Extern on port 5006...
start "Agent Dependent" cmd /c "cd agents && python AgentDependent.py"

:: Start Client
echo Starting Client on port 5006...
start "Client" cmd /c "cd agents && python Client.py"

:: Start Recomanador
echo Starting Recomanador on port 5010...
start "Agent Recomanador" cmd /c "cd agents && python AgentRecomanador.py"

:: Wait a bit to ensure all agents start
timeout /t 2 /nobreak > NUL

echo All services are up and running.
echo Directory Service running at http://localhost:5000
echo Agent 1 running at http://localhost:5001
echo Agent 2 running at http://localhost:5002
echo Agent Venedor running at http://localhost:5003
echo Agent Extern running at http://localhost:5004
echo Agent Valoracions running at http://localhost:5005
echo Agent Dependent running at http://localhost:5006
echo Client running at http://localhost:5007
echo Agent Recomanador running at http://localhost:5010
pause
