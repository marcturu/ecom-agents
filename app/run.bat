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

:: Wait a bit to ensure all agents start
timeout /t 2 /nobreak > NUL

echo All services are up and running.
echo Directory Service running at http://localhost:5000
echo Agent 1 running at http://localhost:5001
echo Agent 2 running at http://localhost:5002
pause
