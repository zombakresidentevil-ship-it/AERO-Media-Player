@echo off
cd /d %~dp0
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File build_win.ps1
pause
