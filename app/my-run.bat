@echo off
cd ..
REM Start the directory service
start "Directory Service" cmd /c "python -m app.MyAgents.simple_directory"
timeout /t 1

REM Start all agents
start "Logistic Center Administrator Agent" cmd /c "python -m app.MyAgents.LogisticCenterAdministratorAgent"
timeout /t 1
start "Logistic Center Agent" cmd /c "python -m app.MyAgents.LogisticCenterAgent"
timeout /t 1
start "Interface Agent" cmd /c "python -m app.MyAgents.interface_agent"
timeout /t 1
start "EnregistradorValoracions Agent" cmd /c "python -m app.MyAgents.AgentEnregistradorValoracions"
timeout /t 1

REM Wait for user input before stopping all agents
pause

cd app
REM Run the stopping program
python stop_agents.py

