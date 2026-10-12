@echo off
REM ND Engenharia - instala o ambiente Python do repositorio (rodar uma vez)
cd /d "%~dp0"
py -3.12 -m venv .venv || python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e "nd_estruturas[dev]"
echo.
echo Pronto. Para abrir as ferramentas, de dois cliques em abrir_ferramentas.bat
pause
