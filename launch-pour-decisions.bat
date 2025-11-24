@echo off
setlocal
cd /d "%~dp0\pour-decisions"

if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)

python main.py
