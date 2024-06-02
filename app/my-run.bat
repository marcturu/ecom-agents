@echo off
cd ..
REM Start the directory service
start "Directory Service" cmd /c "python -m app.MyAgents.simple_directory"
timeout /t 1

REM Start all agents
start "Logistic Center Administrator Agent" cmd /c "python -m app.MyAgents.logistic_center_administrator_agent"
timeout /t 1
start "Lots Administrator Agent" cmd /c "python -m app.MyAgents.lots_administrator_agent"
timeout /t 1
start "Interface Agent" cmd /c "python -m app.MyAgents.interface_agent"
timeout /t 1

REM Wait for user input before stopping all agents
pause

cd app
REM Run the stopping program
python stop_agents.py

