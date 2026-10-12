@echo off
REM ND Engenharia - atualiza do GitHub e abre as ferramentas no navegador
cd /d "%~dp0"
git pull
call .venv\Scripts\activate
streamlit run streamlit_app.py
