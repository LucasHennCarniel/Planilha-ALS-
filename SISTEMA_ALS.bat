@echo off
chcp 65001 >nul
title Sistema de Manutenção ALS - Gerenciador Completo
color 0A
cls

REM ════════════════════════════════════════════════════════════
REM   SISTEMA DE MANUTENÇÃO ALS - EXECUTÁVEL ÚNICO
REM   Detecta automaticamente o que precisa ser feito
REM ════════════════════════════════════════════════════════════

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         SISTEMA DE GESTÃO DE MANUTENÇÃO - ALS            ║
echo ║                  Gerenciador Automático                    ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ════════════════════════════════════════════════════════════
REM ETAPA 1: DETECTAR MODO DE OPERAÇÃO
REM ════════════════════════════════════════════════════════════

REM Verifica se já existe executável pronto
if exist "dist\SistemaManutencaoALS.exe" (
    echo  Executável já existe!
    echo.
    echo Escolha uma opção:
    echo.
    echo [1] Executar o sistema direto (.exe standalone)
    echo [2] Recriar o executável (se fez mudanças no código)
    echo [3] Executar em modo desenvolvimento (Python)
    echo [4] Sair
    echo.
    choice /C 1234 /N /M "Digite o número da opção: "
    
    if errorlevel 4 exit /b 0
    if errorlevel 3 goto :modo_desenvolvimento
    if errorlevel 2 goto :rebuild_exe
    if errorlevel 1 goto :executar_exe
)

REM Se não existe executável, verifica se Python está instalado
echo [INFO] Verificando ambiente...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  Python não está instalado!
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║  PARA USAR ESTE SISTEMA, VOCÊ PRECISA DE PYTHON          ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo Opção 1: INSTALAÇÃO COMPLETA (Recomendado)
    echo ──────────────────────────────────────────────────────────
    echo 1. Instale Python 3.8+ de: https://www.python.org/downloads/
    echo 2. ️  IMPORTANTE: Marque "Add Python to PATH" na instalação
    echo 3. Execute este arquivo novamente
    echo.
    echo Opção 2: USAR EXECUTÁVEL PRONTO (Mais Simples)
    echo ──────────────────────────────────────────────────────────
    echo Se alguém já criou o executável (.exe), basta copiar:
    echo • dist\SistemaManutencaoALS.exe
    echo • pasta data\
    echo E executar o .exe direto!
    echo.
    pause
    exit /b 1
)

echo  Python encontrado: 
python --version
echo.

REM ════════════════════════════════════════════════════════════
REM ETAPA 2: VERIFICAR SE DEPENDÊNCIAS JÁ ESTÃO INSTALADAS
REM ════════════════════════════════════════════════════════════

echo [INFO] Verificando dependências instaladas...
echo.

pip show pandas >nul 2>&1
set PANDAS_OK=%errorlevel%

pip show openpyxl >nul 2>&1
set OPENPYXL_OK=%errorlevel%

pip show pyinstaller >nul 2>&1
set PYINSTALLER_OK=%errorlevel%

pip show tkcalendar >nul 2>&1
set TKCALENDAR_OK=%errorlevel%

pip show pillow >nul 2>&1
set PILLOW_OK=%errorlevel%

if %PANDAS_OK%==0 if %OPENPYXL_OK%==0 if %PYINSTALLER_OK%==0 if %TKCALENDAR_OK%==0 if %PILLOW_OK%==0 (
    echo [OK] Todas as dependências já estão instaladas!
    echo.
    goto :executar_direto
) else (
    echo [AVISO] Algumas dependências estão faltando.
    echo.
    goto :instalar_dependencias_auto
)

REM ════════════════════════════════════════════════════════════
REM ETAPA 3: INSTALAR DEPENDÊNCIAS AUTOMATICAMENTE
REM ════════════════════════════════════════════════════════════

:instalar_dependencias_auto
echo ╔════════════════════════════════════════════════════════════╗
echo ║         INSTALAÇÃO AUTOMÁTICA DE DEPENDÊNCIAS            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Instalando dependências necessárias...
echo [INFO] Isso será feito APENAS UMA VEZ
echo [INFO] Tempo estimado: 2-5 minutos
echo.

echo [1/4] Atualizando pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [AVISO] Não foi possível atualizar o pip, continuando...
) else (
    echo [OK] Pip atualizado
)
echo.

echo [2/4] Instalando bibliotecas necessárias...
echo (Aguarde, isso pode demorar alguns minutos)
echo.
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependências!
    echo.
    echo Possíveis soluções:
    echo 1. Verifique sua conexão com a internet
    echo 2. Execute como Administrador
    echo 3. Tente instalar manualmente: pip install pandas openpyxl pyinstaller tkcalendar pillow
    echo.
    pause
    exit /b 1
)
echo [OK] Bibliotecas instaladas com sucesso!
echo.

echo [3/4] Criando estrutura de pastas...
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "backup" mkdir backup
if not exist "src" mkdir src
echo [OK] Estrutura criada!
echo.

echo [4/4] Verificando instalação...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Verificação falhou!
    pause
    exit /b 1
)
echo [OK] Tudo pronto!
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║         INSTALAÇÃO CONCLUÍDA COM SUCESSO!                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Iniciando o sistema automaticamente...
timeout /t 2 >nul
goto :executar_direto

REM ════════════════════════════════════════════════════════════
REM EXECUTAR SISTEMA DIRETO (APÓS VERIFICAÇÃO)
REM ════════════════════════════════════════════════════════════

:executar_direto
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║               SISTEMA DE MANUTENÇÃO ALS                  ║
echo ║                   INICIANDO SISTEMA...                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Cria pastas se não existirem
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "backup" mkdir backup

REM Verifica se o arquivo principal existe
if not exist "src\main.py" (
    echo [ERRO] Arquivo src\main.py não encontrado!
    echo.
    echo Verifique se a estrutura do projeto está correta.
    echo.
    pause
    goto :menu_principal
)

echo [OK] Ambiente configurado
echo [OK] Dependências verificadas
echo [INFO] Abrindo interface gráfica...
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  O sistema será aberto em uma nova janela.                ║
echo ║  Não feche esta janela até terminar de usar o sistema.    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

python -m src.main

if errorlevel 1 (
    echo.
    echo [ERRO] O sistema foi encerrado com erro.
    echo.
    echo Possíveis causas:
    echo - Arquivo de dados corrompido
    echo - Dependência faltando
    echo - Erro no código
    echo.
    echo Deseja:
    echo [1] Tentar novamente
    echo [2] Reinstalar dependências
    echo [3] Ir ao menu principal
    echo [4] Sair
    echo.
    choice /C 1234 /N /M "Escolha uma opção: "
    if errorlevel 4 exit /b 1
    if errorlevel 3 goto :menu_principal
    if errorlevel 2 goto :reinstalar
    if errorlevel 1 goto :executar_direto
) else (
    echo.
    echo [OK] Sistema encerrado normalmente.
    echo.
    echo Deseja:
    echo [1] Executar novamente
    echo [2] Ir ao menu principal
    echo [3] Sair
    echo.
    choice /C 123 /N /M "Escolha uma opção: "
    if errorlevel 3 exit /b 0
    if errorlevel 2 goto :menu_principal
    if errorlevel 1 goto :executar_direto
)

REM ════════════════════════════════════════════════════════════
REM OPÇÃO ANTIGA: INSTALAR COM CONFIRMAÇÃO (mantida para menu)
REM ════════════════════════════════════════════════════════════

:instalar_dependencias
echo ╔════════════════════════════════════════════════════════════╗
echo ║            INSTALAÇÃO DE DEPENDÊNCIAS                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Isso será feito APENAS UMA VEZ.
echo Tempo estimado: 2-5 minutos
echo.

choice /C SN /N /M "Deseja instalar as dependências agora? (S/N): "
if errorlevel 2 (
    echo.
    echo [INFO] Instalação cancelada.
    echo O sistema não pode funcionar sem as dependências.
    echo.
    pause
    exit /b 1
)

goto :instalar_dependencias_auto

REM ════════════════════════════════════════════════════════════
REM MENU PRINCIPAL
REM ════════════════════════════════════════════════════════════

:menu_principal
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         SISTEMA DE GESTÃO DE MANUTENÇÃO - ALS            ║
echo ║                      MENU PRINCIPAL                        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Escolha uma opção:
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │  [1] [PLAY] Executar Sistema                             │
echo │      └─ Inicia o sistema direto                           │
echo │                                                            │
echo │  [2] [BUILD] Criar Executável (.exe)                     │
echo │      └─ Para rodar sem Python (entregar para usuário)     │
echo │                                                            │
echo │  [3] [EXE] Executar o Executável (.exe)                  │
echo │      └─ Testa o .exe criado                                │
echo │                                                            │
echo │  [4] [REPAIR] Reinstalar Dependências                    │
echo │      └─ Se algo deu errado                                 │
echo │                                                            │
echo │  [5] [INFO] Mostrar Informações do Sistema               │
echo │                                                            │
echo │  [6] [EXIT] Sair                                          │
echo └────────────────────────────────────────────────────────────┘
echo.

choice /C 123456 /N /M "Digite o número da opção: "

if errorlevel 6 goto :sair
if errorlevel 5 goto :mostrar_info
if errorlevel 4 goto :reinstalar
if errorlevel 3 goto :executar_exe
if errorlevel 2 goto :criar_executavel
if errorlevel 1 goto :modo_desenvolvimento

REM ════════════════════════════════════════════════════════════
REM OPÇÃO 1: MODO DESENVOLVIMENTO (do menu)
REM ════════════════════════════════════════════════════════════

:modo_desenvolvimento
goto :executar_direto

REM ════════════════════════════════════════════════════════════
REM OPÇÃO 2: CRIAR EXECUTÁVEL
REM ════════════════════════════════════════════════════════════

:criar_executavel
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║               CRIANDO EXECUTÁVEL (.EXE)                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:rebuild_exe
echo ️  ATENÇÃO: Este processo pode demorar 5-15 minutos!
echo.
echo O executável criado funcionará SEM precisar de Python.
echo Perfeito para entregar ao usuário final.
echo.

choice /C SN /N /M "Deseja continuar? (S/N): "
if errorlevel 2 goto :menu_principal

echo.
echo [1/4] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ️  PyInstaller não encontrado, instalando...
    pip install pyinstaller --quiet
    echo  PyInstaller instalado
) else (
    echo  PyInstaller OK
)
echo.

echo [2/4] Limpando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec
echo  Limpeza concluída
echo.

echo [3/4] Criando executável standalone (arquivo único)...
echo (Este é o passo mais demorado, aguarde 5-15 minutos...)
echo.
echo [INFO] Empacotando TUDO em um único .exe:
echo   - Código Python completo
echo   - Todas as bibliotecas (pandas, openpyxl, tkinter...)
echo   - Interface gráfica
echo   - Python Runtime embutido
echo.

pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "SistemaManutencaoALS" ^
    --icon=NONE ^
    --clean ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=tkinter ^
    --hidden-import=tkcalendar ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --collect-all=pandas ^
    --collect-all=openpyxl ^
    --collect-all=tkcalendar ^
    --collect-all=PIL ^
    --collect-submodules=tkinter ^
    src\main.py

if errorlevel 1 (
    echo.
    echo  ERRO ao criar executável!
    echo.
    echo Possíveis soluções:
    echo 1. Execute como Administrador
    echo 2. Desative o antivírus temporariamente
    echo 3. Libere espaço em disco
    echo.
    pause
    goto :menu_principal
)

echo.
echo [4/4] Verificando resultado...

if exist "dist\SistemaManutencaoALS.exe" (
    echo [OK] Executável criado com sucesso!
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║         EXECUTÁVEL STANDALONE CRIADO!                    ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo [INFO] Arquivo criado em:
    echo    dist\SistemaManutencaoALS.exe
    echo.
    echo [INFO] Este é um arquivo ÚNICO e STANDALONE contendo:
    echo    ✓ Python completo embutido
    echo    ✓ Todas as bibliotecas (pandas, openpyxl, tkinter...)
    echo    ✓ Todo o código da aplicação
    echo    ✓ Interface gráfica completa
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║         COMO ENVIAR PARA SEU PAI                         ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo OPÇÃO 1 - APENAS O .EXE (mais simples):
    echo ───────────────────────────────────────────────────────────
    echo   Envie: dist\SistemaManutencaoALS.exe
    echo   Sistema cria planilha vazia automaticamente
    echo.
    echo OPÇÃO 2 - .EXE + PLANILHA (recomendado):
    echo ───────────────────────────────────────────────────────────
    echo   Copie:
    echo     - dist\SistemaManutencaoALS.exe
    echo     - data\PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx
    echo.
    echo   Na máquina dele:
    echo     Pasta qualquer\
    echo     ├── SistemaManutencaoALS.exe
    echo     └── data\
    echo         └── planilha.xlsx
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║  ELE NÃO PRECISA DE NADA INSTALADO!                     ║
    echo ║    ✗ Python                                              ║
    echo ║    ✗ Bibliotecas                                         ║
    echo ║    ✗ Internet                                            ║
    echo ║    ✗ Arquivos .bat, .py, src/, etc                       ║
    echo ║                                                            ║
    echo ║  Apenas duplo clique e funciona!                         ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    
    choice /C SN /N /M "Deseja abrir a pasta com o executável? (S/N): "
    if errorlevel 2 goto :apos_criar_exe
    if errorlevel 1 explorer dist
    
    :apos_criar_exe
    echo.
    choice /C SN /N /M "Deseja testar o executável agora? (S/N): "
    if errorlevel 2 (
        pause
        goto :menu_principal
    )
    if errorlevel 1 goto :executar_exe
) else (
    echo  Erro: Executável não foi criado!
    echo.
    pause
    goto :menu_principal
)

REM ════════════════════════════════════════════════════════════
REM OPÇÃO 3: EXECUTAR EXECUTÁVEL
REM ════════════════════════════════════════════════════════════

:executar_exe
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║            ▶️  EXECUTANDO .EXE STANDALONE                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

if not exist "dist\SistemaManutencaoALS.exe" (
    echo  Executável não encontrado!
    echo.
    echo O arquivo dist\SistemaManutencaoALS.exe não existe.
    echo.
    echo Você precisa criar o executável primeiro (opção 2).
    echo.
    pause
    goto :menu_principal
)

echo  Executável encontrado
echo.
echo  Iniciando sistema em modo standalone...
echo    (Pode demorar 5-15 segundos na primeira execução)
echo.

start "" "dist\SistemaManutencaoALS.exe"

echo  Sistema iniciado!
echo.
echo A janela do sistema foi aberta separadamente.
echo Você pode fechar esta janela ou aguardar.
echo.
pause
goto :menu_principal

REM ════════════════════════════════════════════════════════════
REM OPÇÃO 4: REINSTALAR DEPENDÊNCIAS
REM ════════════════════════════════════════════════════════════

:reinstalar
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           REINSTALAR DEPENDÊNCIAS                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Isso irá reinstalar todas as bibliotecas do zero.
echo Útil se algo deu errado na instalação anterior.
echo.

choice /C SN /N /M "Deseja continuar? (S/N): "
if errorlevel 2 goto :menu_principal

echo.
echo Desinstalando pacotes antigos...
pip uninstall -y pandas openpyxl pyinstaller tkcalendar pillow >nul 2>&1
echo  Limpeza concluída
echo.

goto :instalar_dependencias

REM ════════════════════════════════════════════════════════════
REM OPÇÃO 5: MOSTRAR INFORMAÇÕES
REM ════════════════════════════════════════════════════════════

:mostrar_info
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║               INFORMAÇÕES DO SISTEMA                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo  AMBIENTE:
echo ───────────────────────────────────────────────────────────
python --version 2>nul || echo Python:  Não instalado
pip --version 2>nul || echo Pip:  Não instalado
echo.

echo  DEPENDÊNCIAS:
echo ───────────────────────────────────────────────────────────
pip show pandas >nul 2>&1 && echo Pandas:  Instalado || echo Pandas:  Não instalado
pip show openpyxl >nul 2>&1 && echo OpenPyXL:  Instalado || echo OpenPyXL:  Não instalado
pip show pyinstaller >nul 2>&1 && echo PyInstaller:  Instalado || echo PyInstaller:  Não instalado
pip show tkcalendar >nul 2>&1 && echo TkCalendar:  Instalado || echo TkCalendar:  Não instalado
pip show pillow >nul 2>&1 && echo Pillow:  Instalado || echo Pillow:  Não instalado
echo.

echo  ESTRUTURA:
echo ───────────────────────────────────────────────────────────
if exist "src\main.py" (echo src\main.py:  Existe) else (echo src\main.py:  Não encontrado)
if exist "src\database.py" (echo src\database.py:  Existe) else (echo src\database.py:  Não encontrado)
if exist "src\utils.py" (echo src\utils.py:  Existe) else (echo src\utils.py:  Não encontrado)
if exist "data" (echo Pasta data\:  Existe) else (echo Pasta data\:  Não encontrada)
if exist "dist\SistemaManutencaoALS.exe" (echo Executável:  Criado) else (echo Executável:  Não criado)
echo.

echo  ARQUIVOS DE DADOS:
echo ───────────────────────────────────────────────────────────
if exist "data\PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx" (
    echo Planilha principal:  Encontrada
) else (
    echo Planilha principal: ️  Não encontrada
    echo    O sistema criará uma vazia ao executar
)
echo.

echo  BACKUPS:
echo ───────────────────────────────────────────────────────────
if exist "backup" (
    dir /b backup\*.xlsx 2>nul | find /c ".xlsx" > nul
    if errorlevel 1 (
        echo Nenhum backup encontrado
    ) else (
        echo Backups disponíveis:
        dir /b backup\*.xlsx 2>nul
    )
) else (
    echo Pasta backup não encontrada
)
echo.

echo  DOCUMENTAÇÃO:
echo ───────────────────────────────────────────────────────────
if exist "README.md" (echo README.md: ) else (echo README.md: )
if exist "GUIA_DO_USUARIO.txt" (echo GUIA_DO_USUARIO.txt: ) else (echo GUIA_DO_USUARIO.txt: )
if exist "FAQ.txt" (echo FAQ.txt: ) else (echo FAQ.txt: )
echo.

echo ═══════════════════════════════════════════════════════════
echo.
pause
goto :menu_principal

REM ════════════════════════════════════════════════════════════
REM SAIR
REM ════════════════════════════════════════════════════════════

:sair
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║               Até logo!                                  ║
echo ║                                                            ║
echo ║         Sistema de Manutenção ALS - v1.0                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
timeout /t 2 >nul
exit /b 0
