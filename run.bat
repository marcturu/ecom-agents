@echo off
cd /d %~dp0

REM Activate the virtual environment
call .venv\Scripts\activate

REM Go to the app directory
cd app

REM Call the app's run.bat that starts all agents
call run.bat

REM Return to root
cd ..

pause