@echo off
title Iniciando Sistema ALS...
color 0B

echo ===================================
echo   Iniciando Sistema de Manutencao
echo ===================================
echo.
echo Verificando dependencias...
python -c "import pandas, tkcalendar, openpyxl, reportlab" 2>nul
if errorlevel 1 (
    echo Instalando pacotes necessarios...
    pip install pandas openpyxl reportlab tkcalendar pillow >nul
)

echo Iniciando o programa...
python src\main.py

if errorlevel 1 (
    echo.
    echo O programa encontrou um erro e foi fechado.
    pause
)
