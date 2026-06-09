@echo off
title SymptoPy
cd /d %~dp0
echo.
echo  ⚕ SYMPTOOPY - Iniciando...
echo  Aguarde o navegador abrir automaticamente.
echo.
pip install streamlit --quiet 2>nul
streamlit run interface.py --server.port 8501 --server.headless false
pause
