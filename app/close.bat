@echo off

:: Function to kill processes by port number
setlocal enabledelayedexpansion

set "ports=5000 5001 5002 5003 5004"

for %%p in (%ports%) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p') do (
        echo Killing process on port %%p with PID %%a
        taskkill /PID %%a /F
    )
)

endlocal

echo All agents and the directory service have been terminated.
pause
