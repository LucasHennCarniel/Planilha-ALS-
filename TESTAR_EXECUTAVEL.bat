@echo off
chcp 65001 >nul
title Teste do Sistema - Verificar Banco de Dados
color 0B

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║       TESTE DE BANCO DE DADOS - SISTEMA ALS           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

echo [1/4] Verificando banco de dados atual...
echo.

if exist "data\sistema_als.db" (
    echo ✅ Banco de dados encontrado: data\sistema_als.db
    dir "data\sistema_als.db"
    echo.
) else (
    echo ❌ Banco de dados NÃO encontrado!
    pause
    exit /b 1
)

echo [2/4] Verificando estrutura do banco...
echo.

python -c "import sqlite3; conn = sqlite3.connect('data/sistema_als.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM manutencoes'); print(f'✅ Registros de manutenção: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM veiculos WHERE ativo=1'); print(f'✅ Veículos ativos: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM destinos WHERE ativo=1'); print(f'✅ Destinos ativos: {cursor.fetchone()[0]}'); conn.close()"

echo.
echo [3/4] Testando sistema em Python...
echo.
echo Abrindo sistema... (Feche para continuar)
python src/main.py

echo.
echo [4/4] Agora vamos gerar o executável...
echo.
pause

call GERAR_SISTEMA.bat

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║           ✅ TESTE COMPLETO FINALIZADO!               ║
echo ╚════════════════════════════════════════════════════════╝
echo.
pause
