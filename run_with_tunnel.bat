@echo off
setlocal

REM 1) Ouvre un tunnel SSH vers PythonAnywhere (nouvelle fenêtre)
start "PA Tunnel" powershell -NoExit -Command ^
  ssh -N -L 3307:stephanefly.mysql.pythonanywhere-services.com:3306 stephanefly@ssh.pythonanywhere.com

REM 2) Petite pause pour laisser le tunnel démarrer
timeout /t 3 >nul

REM 3) Active le venv et lance FastAPI
REM call .venv\Scripts\activate
REM uvicorn main:app --reload

endlocal
