@echo off
cd /d "%~dp0nd_estruturas"
call ..\.venv\Scripts\activate
pytest -q
pause
