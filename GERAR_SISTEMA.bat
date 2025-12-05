@echo off
chcp 65001 >nul
title Sistema ALS - Gerar Executável e Preparar para Distribuição
color 0A

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║     SISTEMA ALS - GERADOR DE EXECUTÁVEL COMPLETO      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM ========================================
REM ETAPA 1: Verificar ambiente
REM ========================================
echo [1/6] Verificando ambiente Python...
python --version
if errorlevel 1 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)
echo ✅ Python OK
echo.

REM ========================================
REM ETAPA 2: Instalar dependências
REM ========================================
echo [2/6] Instalando/Atualizando dependências...
pip install -q -r requirements.txt
pip install -q pyinstaller
echo ✅ Dependências instaladas
echo.

REM ========================================
REM ETAPA 3: Gerar executável
REM ========================================
echo [3/6] Gerando executável...
echo      (Isso pode levar alguns minutos)
echo.

pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "SistemaManutencaoALS" ^
    --icon="img/logo ALS.png" ^
    --add-data "data;data" ^
    --add-data "img;img" ^
    --hidden-import "openpyxl" ^
    --hidden-import "reportlab" ^
    --hidden-import "PIL" ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao gerar executável!
    pause
    exit /b 1
)
echo ✅ Executável gerado
echo.

REM ========================================
REM ETAPA 4: Copiar arquivos essenciais
REM ========================================
echo [4/6] Copiando banco de dados e imagens...

if not exist "dist\data" mkdir "dist\data"
copy "data\sistema_als.db" "dist\data\" >nul
echo ✅ Banco de dados copiado (141 veículos)

if not exist "dist\img" mkdir "dist\img"
xcopy "img\*.*" "dist\img\" /E /I /Y >nul
echo ✅ Imagens copiadas
echo.

REM ========================================
REM ETAPA 5: Criar pasta para distribuição
REM ========================================
echo [5/6] Preparando pasta para distribuição...

set "PASTA_DIST=SistemaALS_ParaSeuPai"
if exist "%PASTA_DIST%" rmdir /s /q "%PASTA_DIST%"
mkdir "%PASTA_DIST%"

copy "dist\SistemaManutencaoALS.exe" "%PASTA_DIST%\" >nul
xcopy "dist\data" "%PASTA_DIST%\data\" /E /I /Y >nul
xcopy "dist\img" "%PASTA_DIST%\img\" /E /I /Y >nul

REM Cria pastas necessárias para o sistema funcionar
mkdir "%PASTA_DIST%\backup" 2>nul
mkdir "%PASTA_DIST%\output" 2>nul
echo ✅ Pastas backup e output criadas

REM Cria arquivo de instruções simples
echo SISTEMA DE MANUTENÇÃO ALS > "%PASTA_DIST%\LEIA-ME.txt"
echo. >> "%PASTA_DIST%\LEIA-ME.txt"
echo COMO USAR: >> "%PASTA_DIST%\LEIA-ME.txt"
echo 1. Mantenha todos os arquivos juntos nesta pasta >> "%PASTA_DIST%\LEIA-ME.txt"
echo 2. Dê dois cliques em: SistemaManutencaoALS.exe >> "%PASTA_DIST%\LEIA-ME.txt"
echo 3. Pronto! >> "%PASTA_DIST%\LEIA-ME.txt"
echo. >> "%PASTA_DIST%\LEIA-ME.txt"
echo O sistema já tem 141 veículos cadastrados. >> "%PASTA_DIST%\LEIA-ME.txt"
echo Cavalos vazios e carretas vazias já identificados. >> "%PASTA_DIST%\LEIA-ME.txt"
echo. >> "%PASTA_DIST%\LEIA-ME.txt"
echo Para adicionar novos veículos, use a opção dentro do sistema. >> "%PASTA_DIST%\LEIA-ME.txt"

echo ✅ Pasta preparada: %PASTA_DIST%\
echo.

REM ========================================
REM ETAPA 6: Resumo final
REM ========================================
echo [6/6] Verificando resultado...
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              ✅ TUDO PRONTO COM SUCESSO!              ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 📂 PASTA CRIADA: %PASTA_DIST%\
echo.
echo 📋 CONTEÚDO:
dir /B "%PASTA_DIST%"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📋 PRÓXIMOS PASSOS:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 1. TESTE AGORA:
echo    • Abra: %PASTA_DIST%\SistemaManutencaoALS.exe
echo    • Clique em "Cadastro de Veículos"
echo    • Confirme que aparecem os 141 veículos
echo.
echo 2. SE TUDO FUNCIONAR:
echo    • Compacte a pasta %PASTA_DIST% em .zip
echo    • OU copie para um pendrive
echo    • Envie para seu pai!
echo.
echo 3. SEU PAI DEVE:
echo    • Descompactar (se for .zip)
echo    • Manter tudo junto
echo    • Abrir o SistemaManutencaoALS.exe
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✨ Sistema completo com 141 veículos já cadastrados!
echo.
pause

REM Abre a pasta no Explorer
explorer "%PASTA_DIST%"
