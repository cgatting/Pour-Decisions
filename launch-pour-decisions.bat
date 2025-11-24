@echo off
REM Quick launcher for the Pour Decisions dev server.
cd /d "%~dp0\pour-decisions"
npm run dev -- --host
