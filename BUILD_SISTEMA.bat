@echo off
chcp 65001 >nul
title Sistema ALS - Gerador de Executável
color 0B

:MENU
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║            SISTEMA ALS - GERADOR DE EXECUTÁVEL                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo  📋 ESCOLHA UMA OPÇÃO:
echo.
echo  ┌────────────────────────────────────────────────────────────┐
echo  │  [1] 🚀 GERAR EXECUTÁVEL ATUALIZADO                        │
echo  │      └─ Busca código mais recente e compila (30-60 seg)   │
echo  └────────────────────────────────────────────────────────────┘
echo.
echo  ┌────────────────────────────────────────────────────────────┐
echo  │  [2] 🔍 VERIFICAR AMBIENTE                                 │
echo  │      └─ Diagnóstico do sistema (Python, pacotes, etc)     │
echo  └────────────────────────────────────────────────────────────┘
echo.
echo  ┌────────────────────────────────────────────────────────────┐
echo  │  [3] 🧹 LIMPAR CACHE                                       │
echo  │      └─ Remove builds antigos e cache                      │
echo  └────────────────────────────────────────────────────────────┘
echo.
echo  ┌────────────────────────────────────────────────────────────┐
echo  │  [0] ❌ SAIR                                               │
echo  └────────────────────────────────────────────────────────────┘
echo.
echo ════════════════════════════════════════════════════════════════
set /p opcao=" Digite o número da opção: "
echo ════════════════════════════════════════════════════════════════

if "%opcao%"=="1" goto GERAR_EXECUTAVEL
if "%opcao%"=="2" goto VERIFICAR_AMBIENTE
if "%opcao%"=="3" goto LIMPAR_CACHE
if "%opcao%"=="0" goto SAIR

echo.
echo ❌ Opção inválida! Tente novamente.
timeout /t 2 >nul
goto MENU

REM ════════════════════════════════════════════════════════════════
REM OPÇÃO 1: GERAR EXECUTÁVEL ATUALIZADO
REM ════════════════════════════════════════════════════════════════
:GERAR_EXECUTAVEL
cls
set "INICIO=%TIME%"
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          🚀 GERANDO EXECUTÁVEL COM CÓDIGO ATUALIZADO           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 💡 Este processo irá:
echo    • Buscar todas as modificações do código
echo    • Limpar cache antigo
echo    • Recompilar com as últimas atualizações
echo    • Gerar executável pronto para uso
echo.
echo ⏱️  Início: %TIME%
echo ⏱️  Tempo estimado: 30-60 segundos
echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM [1/6] Verificar Python
echo [1/6] 🐍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo    ❌ Python não encontrado!
    echo.
    echo    Solução:
    echo    1. Instale Python 3.8 ou superior
    echo    2. https://www.python.org/downloads/
    echo.
    pause
    goto MENU
)
for /f "tokens=*" %%i in ('python --version') do echo    ✅ %%i
echo.

REM [2/6] Verificar PyInstaller
echo [2/6] 📦 Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo    ⚠️  PyInstaller não encontrado. Instalando...
    pip install -q pyinstaller
    echo    ✅ PyInstaller instalado
) else (
    echo    ✅ PyInstaller OK
)
echo.

REM [3/6] Limpar cache (rápido)
echo [3/6] 🧹 Limpando builds antigos...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist SistemaManutencaoALS.spec del SistemaManutencaoALS.spec 2>nul
echo    ✅ Cache limpo
echo.

REM [4/6] Compilar código atualizado
echo [4/6] ⚙️  Compilando código mais recente...
echo    💡 Buscando todas as modificações em src\*.py
echo    ⏱️  AGUARDE: Este processo demora 30-60 segundos
echo    📊 Progresso do PyInstaller será mostrado abaixo:
echo.

set "INICIO_BUILD=%TIME%"
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "SistemaManutencaoALS" ^
    --icon="img/logo ALS.png" ^
    --add-data "img;img" ^
    --hidden-import "openpyxl" ^
    --hidden-import "reportlab" ^
    --hidden-import "PIL" ^
    --hidden-import "pandas" ^
    --hidden-import "tkcalendar" ^
    --log-level WARN ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║              ❌ ERRO AO GERAR EXECUTÁVEL                       ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo Possíveis causas:
    echo   • Erro de sintaxe no código Python
    echo   • PyInstaller desatualizado
    echo   • Antivírus bloqueando compilação
    echo.
    echo Soluções:
    echo   1. Execute opção [2] Verificar Ambiente
    echo   2. Verifique erros no código com: python src/main.py
    echo   3. Tente opção [3] Limpar Cache e depois [1] novamente
    echo.
    pause
    goto MENU
)

echo.
echo    ✅ Compilação concluída!
echo    ⏱️  Tempo: de %INICIO_BUILD% até %TIME%
echo.

REM [5/6] Preparar arquivos
echo [5/6] 📂 Copiando arquivos essenciais...

REM Criar pastas se não existirem
if not exist "dist\data" (
    mkdir "dist\data"
    echo    📁 Pasta dist\data criada
)
if not exist "dist\img" (
    mkdir "dist\img"
    echo    📁 Pasta dist\img criada
)

REM Copia banco de dados COM VEÍCULOS (141 veículos cadastrados)
echo.
echo    📋 Copiando banco de dados com 141 veículos...
if exist "data\sistema_als.db" (
    copy /Y "data\sistema_als.db" "dist\data\sistema_als.db" >nul
    if exist "dist\data\sistema_als.db" (
        echo    ✅ Banco de dados copiado com sucesso!
    ) else (
        echo    ❌ ERRO: Banco NÃO foi copiado!
        echo    💡 Tentando copiar novamente...
        copy "data\sistema_als.db" "dist\data\sistema_als.db"
        pause
    )
) else (
    echo    ❌ ERRO: Banco data\sistema_als.db não encontrado!
    echo    📂 Arquivos em data\:
    dir data\*.db
    pause
)

REM Copia imagens
if exist "img" (
    xcopy "img\*.*" "dist\img\" /E /I /Y /Q >nul 2>&1
    echo    ✅ Imagens copiadas
)
echo.

REM [6/6] Criar pasta final
echo [6/6] 📦 Criando pasta de distribuição...
set "PASTA_DIST=SistemaALS_Atualizado"
if exist "%PASTA_DIST%" (
    echo    🗑️  Removendo pasta antiga...
    rmdir /s /q "%PASTA_DIST%"
)
mkdir "%PASTA_DIST%"
mkdir "%PASTA_DIST%\data"
mkdir "%PASTA_DIST%\img"
echo    ✅ Pastas criadas


REM Cria pastas necessárias para o sistema rodar
mkdir "%PASTA_DIST%\backup" 2>nul
mkdir "%PASTA_DIST%\output" 2>nul
echo   ✅ Pastas backup e output criadas



REM Move executável
echo    📦 Movendo executável...
move "dist\SistemaManutencaoALS.exe" "%PASTA_DIST%\" >nul 2>&1
echo    ✅ Executável movido

REM Copia banco com VEÍCULOS
echo    📋 Copiando banco de dados para pasta final...
if exist "dist\data\sistema_als.db" (
    copy /Y "dist\data\sistema_als.db" "%PASTA_DIST%\data\sistema_als.db" >nul
    echo    ✅ Banco copiado para %PASTA_DIST%\data\
) else (
    echo    ❌ ERRO: Banco não encontrado em dist\data\
    echo    💡 Copiando direto da origem...
    copy /Y "data\sistema_als.db" "%PASTA_DIST%\data\sistema_als.db" >nul
)

REM Copia imagens
xcopy "dist\img\*.*" "%PASTA_DIST%\img\" /E /I /Y /Q >nul 2>&1
echo    ✅ Imagens copiadas

REM Criar instruções simples
echo Sistema ALS - Manutenção de Frota > "%PASTA_DIST%\LEIA-ME.txt"
echo Atualizado em: %DATE% %TIME% >> "%PASTA_DIST%\LEIA-ME.txt"
echo Execute: SistemaManutencaoALS.exe >> "%PASTA_DIST%\LEIA-ME.txt"

echo.
REM Verifica se o banco foi copiado E tem veículos
if exist "%PASTA_DIST%\data\sistema_als.db" (
    echo    ✅ Pasta criada: %PASTA_DIST%\ 
    echo    ✅ Banco de dados incluído
    echo.
    echo    🔍 Verificando conteúdo do banco...
    python -c "import sqlite3; conn = sqlite3.connect('%PASTA_DIST%/data/sistema_als.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM veiculos WHERE ativo = 1'); count = cursor.fetchone()[0]; print(f'    ✅ {count} veículos cadastrados no banco'); conn.close()" 2>nul
    if errorlevel 1 (
        echo    ⚠️  Não foi possível verificar veículos (mas banco existe^)
    )
) else (
    echo    ❌ ERRO CRÍTICO: Banco de dados NÃO foi copiado!
    echo    ⚠️  Execute novamente ou copie manualmente de data\sistema_als.db
    echo.
    echo    📂 Arquivos em %PASTA_DIST%\data\:
    dir "%PASTA_DIST%\data" /b
    pause
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          ✅ EXECUTÁVEL GERADO COM SUCESSO!                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo ⏱️  Tempo: de %INICIO% até %TIME%
echo 📂 Pasta: %PASTA_DIST%\
echo.
echo � PRÓXIMO PASSO: Abra a pasta e teste o executável
echo.
set /p abrir="Abrir pasta agora? (S/N): "
if /i "%abrir%"=="S" explorer "%PASTA_DIST%"
pause
goto MENU

REM ════════════════════════════════════════════════════════════════
REM OPÇÃO 2: VERIFICAR AMBIENTE
REM ════════════════════════════════════════════════════════════════
:VERIFICAR_AMBIENTE
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   🔍 VERIFICAÇÃO DO AMBIENTE                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo ┌─ PYTHON ──────────────────────────────────────────────────────┐
python --version 2>nul
if errorlevel 1 (
    echo   ❌ Python não encontrado!
    echo   💡 Instale: https://www.python.org/downloads/
) else (
    echo   ✅ Python instalado
)
echo └───────────────────────────────────────────────────────────────┘
echo.

echo ┌─ PACOTES ESSENCIAIS ──────────────────────────────────────────┐
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   ❌ PyInstaller - NÃO instalado
    echo   💡 Será instalado automaticamente na compilação
) else (
    echo   ✅ PyInstaller - instalado
)

pip show pandas >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  pandas - NÃO instalado
    echo   💡 Execute: pip install pandas
) else (
    echo   ✅ pandas - instalado
)

pip show openpyxl >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  openpyxl - NÃO instalado
    echo   💡 Execute: pip install openpyxl
) else (
    echo   ✅ openpyxl - instalado
)

pip show pillow >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  Pillow - NÃO instalado
    echo   💡 Execute: pip install pillow
) else (
    echo   ✅ Pillow - instalado
)
echo └───────────────────────────────────────────────────────────────┘
echo.

echo ┌─ ARQUIVOS DO PROJETO ─────────────────────────────────────────┐
if exist "src\main.py" (
    echo   ✅ src\main.py encontrado
) else (
    echo   ❌ src\main.py NÃO encontrado (CRÍTICO!)
)

if exist "src\models\manutencao_model.py" (
    echo   ✅ src\models\manutencao_model.py encontrado
) else (
    echo   ⚠️  src\models\manutencao_model.py não encontrado
)

if exist "img\logo ALS.png" (
    echo   ✅ Logo encontrado
) else (
    echo   ⚠️  Logo não encontrado (executável sem ícone)
)

if exist "data" (
    echo   ✅ Pasta data/ existe
) else (
    echo   ℹ️  Pasta data/ será criada automaticamente
)
echo └───────────────────────────────────────────────────────────────┘
echo.

echo ┌─ DIAGNÓSTICO FINAL ───────────────────────────────────────────┐
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo   ❌ SISTEMA NÃO PRONTO
    echo   💡 Instale Python primeiro
) else (
    if exist "src\main.py" (
        echo   ✅ SISTEMA PRONTO PARA COMPILAR!
        echo.
        echo   💡 Use opção [1] para gerar executável
    ) else (
        echo   ❌ SISTEMA NÃO PRONTO
        echo   💡 Arquivo src\main.py não encontrado
    )
)
echo.
echo └───────────────────────────────────────────────────────────────┘
echo.
pause
goto MENU

REM ════════════════════════════════════════════════════════════════
REM OPÇÃO 3: LIMPAR CACHE
REM ════════════════════════════════════════════════════════════════
:LIMPAR_CACHE
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                      🧹 LIMPEZA DE CACHE                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Esta ação irá remover:
echo   • Pasta build/
echo   • Pasta dist/
echo   • Pasta __pycache__/
echo   • Arquivos .spec
echo   • Arquivos .pyc
echo.
echo 💡 Útil quando a compilação falha ou gera erro
echo.
set /p confirma="Deseja continuar? (S/N): "
if /i not "%confirma%"=="S" goto MENU

echo.
echo Executando limpeza...
echo.

if exist build (
    rmdir /s /q build 2>nul
    echo ✅ build/ removido
)

if exist dist (
    rmdir /s /q dist 2>nul
    echo ✅ dist/ removido
)

if exist SistemaManutencaoALS.spec (
    del SistemaManutencaoALS.spec 2>nul
    echo ✅ .spec removido
)

for /d /r %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d" 2>nul
    echo ✅ __pycache__ removido
)

for /r %%i in (*.pyc) do @if exist "%%i" (
    del "%%i" 2>nul
)
echo ✅ Arquivos .pyc removidos

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                 ✅ LIMPEZA CONCLUÍDA!                          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 💡 Agora você pode executar opção [1] para gerar executável limpo
echo.
pause
goto MENU

REM ════════════════════════════════════════════════════════════════
REM OPÇÃO 0: SAIR
REM ════════════════════════════════════════════════════════════════
:SAIR
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    👋 ATÉ LOGO!                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo   Sistema ALS - Gerador de Executável
echo.
echo   💡 Lembre-se:
echo   • Opção [1] gera executável com código atualizado
echo   • Opção [2] verifica se tudo está OK
echo   • Opção [3] limpa cache se houver problemas
echo.
echo   Obrigado por usar o Sistema ALS! 🚗✨
echo.
timeout /t 3 >nul
exit
