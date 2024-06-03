@echo off

:: Function to kill processes by port number
setlocal enabledelayedexpansion

set "ports=9000 9010 9020 9030 5000 5001 5002 5003 5004 5005 5006 5007 5010 5011"

for %%p in (%ports%) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p') do (
        echo Killing process on port %%p with PID %%a
        taskkill /PID %%a /F
    )
)

endlocal

echo All agents and the directory service have been terminated.
pause
