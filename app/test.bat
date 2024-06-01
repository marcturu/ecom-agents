@echo off
cd ..

REM Activate the virtual environment if needed
call .venv\Scripts\activate

REM Run the DirectoryAgent
start "Directory Service"  python -m app.agents.simpleDirectroy

REM Run the agents
start "Agent 1"  python -m app.agents.agent1
start "Agent 2"  python -m app.agents.agent2
start "Interface Agent"  python -m app.agents.interface_agent


