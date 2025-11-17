# Sistema de Gestão de Manutenção de Frota - ALS

Sistema completo com interface gráfica para gerenciar manutenções de veículos.

---

## ESTRUTURA DO PROJETO

```
Manutenção ALS/
├── data/
│   └── PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx
├── src/
│   ├── __init__.py
│   ├── main.py          (interface gráfica)
│   ├── database.py      (gerenciamento de dados)
│   └── utils.py         (funções auxiliares)
├── requirements.txt
├── SISTEMA_ALS.bat              [ARQUIVO ÚNICO - Execute este!]
├── GUIA_DO_USUARIO.txt          [Manual para o usuário]
└── README.md                    [Este arquivo]
```

**Pastas criadas automaticamente:**
- `backup/` - Backups automáticos
- `output/` - Relatórios gerados
- `dist/` - Executável (.exe) criado

---

## COMO USAR

### ARQUIVO ÚNICO - SISTEMA_ALS.bat

**Duplo clique neste arquivo faz TUDO automaticamente:**

```powershell
# Simplesmente execute:
SISTEMA_ALS.bat
```

**O que ele faz:**
- Detecta se Python está instalado
- Verifica e instala dependências (se necessário)
- Mostra menu interativo com opções:
  - [1] Executar o sistema (modo desenvolvimento)
  - [2] Criar executável (.exe) para usuário final
  - [3] Executar o executável criado
  - [4] Reinstalar dependências (se algo deu errado)
  - [5] Mostrar informações do sistema
  - [6] Sair

**Inteligência:**
- Pula instalação se já foi feita antes
- Vai direto ao menu se tudo estiver OK
- Detecta se .exe já existe e oferece executar direto

---

## PARA ENTREGAR AO USUÁRIO FINAL

### **1. Criar o Executável:**

```powershell
# Execute:
SISTEMA_ALS.bat

# No menu, escolha:
[2] Criar Executável (.exe)

# Aguarde 5-15 minutos
# Arquivo criado: dist/SistemaManutencaoALS.exe
```

### **2. Copiar para o Usuário:**

```
Copie estas pastas/arquivos:
├── dist/SistemaManutencaoALS.exe  [O programa]
├── data/                          (com a planilha)
├── GUIA_DO_USUARIO.txt            [Manual]
└── (opcional) backup/, output/    (vazias)
```

### **3. Usuário Final:**

```
Duplo clique em: SistemaManutencaoALS.exe
Sistema funciona SEM instalar Python!
NÃO precisa do arquivo SISTEMA_ALS.bat
```

---

## FUNCIONALIDADES DO SISTEMA

### Automações Implementadas

- **Cálculo Automático de Dias em Manutenção**
  - Se DATA SAÍDA vazia → usa data de hoje
  - Sempre atualizado ao salvar

- **Status Dinâmico**
  - DATA ENTRADA preenchida + DATA SAÍDA vazia = `EM SERVIÇO`
  - Ambas preenchidas = `FINALIZADO`

- **Backup Automático**
  - Cada vez que salva, cria backup na pasta `backup/`
  - Nome: `backup_YYYYMMDD_HHMMSS.xlsx`

### Interface Gráfica

- **Novo Registro**: Adiciona manutenção
- **Editar**: Modifica registro (ou duplo clique)
- **Excluir**: Remove registro
- **Salvar**: Salva no Excel com backup
- **Atualizar**: Recarrega dados
- **Filtros**: Busca por Placa, Veículo, Status
- **Relatório**: Gera estatísticas
- **Exportar**: Salva como novo Excel

### Estatísticas em Tempo Real

- Total de registros
- Veículos em serviço
- Manutenções finalizadas
- Tempo médio de manutenção
- Número de placas únicas

---

## REQUISITOS

### Para Desenvolvimento (sua máquina):
- Windows 7/10/11
- Python 3.8+
- Internet (para instalar bibliotecas)

### Para Usuário Final (máquina do seu pai):
- Windows 7/10/11
- **NÃO precisa de Python**
- **NÃO precisa de internet**

### Bibliotecas (instaladas automaticamente):
```
pandas>=2.0.0
openpyxl>=3.1.0
tkcalendar>=1.6.1
pyinstaller>=6.0.0
pillow>=10.0.0
```

---

## IMPORTANTE

### Estrutura da Planilha Excel

O sistema espera estas colunas:
```
DATA | PLACA | KM | VEÍCULO | DESTINO PROGRAMADO | 
SERVIÇO A EXECUTAR | STATUS | DATA ENTRADA | DATA SAÍDA | 
TOTAL DE DIAS EM MANUTENÇÃO | NR° OF | OBS
```

O sistema adiciona colunas automaticamente se faltarem!

---

## INÍCIO RÁPIDO

### Para Você (Primeira Vez):

```powershell
# 1. Abra PowerShell nesta pasta
cd "c:\Users\lucas\Desktop\sites\Manutenção ALS"

# 2. Execute o arquivo único
.\SISTEMA_ALS.bat

# 3. No menu:
#    - Digite 1 para testar
#    - Digite 2 para criar .exe
```

### Para Seu Pai (Usuário Final):

```
1. Receba o arquivo: SistemaManutencaoALS.exe
2. Duplo clique nele
3. Pronto!
```

---

## ONDE FICAM OS ARQUIVOS

```
data/           -> Planilha principal (leitura/escrita)
backup/         -> Backups automáticos (criada automaticamente)
output/         -> Relatórios e exportações (criada automaticamente)
dist/           -> Executável (.exe) após criação
src/            -> Código-fonte do sistema
```

---

## RESOLUÇÃO DE PROBLEMAS

### **Erro: "Python não encontrado"**
- Instale Python 3.8+ de: https://www.python.org/downloads/
- IMPORTANTE: Marque "Add Python to PATH" durante instalação

### **Erro: "Módulo não encontrado"**
- Execute `SISTEMA_ALS.bat` e escolha opção [4] para reinstalar

### **Erro: "Planilha não encontrada"**
- Coloque a planilha em: `data/PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx`
- Ou o sistema cria uma vazia automaticamente

### **Executável não abre**
- Execute `SISTEMA_ALS.bat` e escolha opção [2] para recriar
- Verifique se a pasta `data` está junto com o .exe
- Tente executar como Administrador

---

## DICAS DE USO

1. **Sempre use o botão "Salvar"** após fazer mudanças
2. **Backup automático** é criado sempre que salva
3. **Duplo clique** em uma linha para editar rapidamente
4. **Filtros** ajudam a encontrar veículos específicos
5. **Status e Dias** são calculados automaticamente

---

## � DOCUMENTAÇÃO ADICIONAL

- **GUIA_DO_USUARIO.txt** - Manual completo para usuário final
- **FAQ.txt** - Perguntas frequentes e soluções
- **README.md** - Este arquivo (documentação técnica)

---

## � CHANGELOG

**v1.0.0** (17/11/2025)
- ✅ Interface gráfica completa
- ✅ Cálculo automático de dias e status
- ✅ Sistema de backup automático
- ✅ Filtros e busca
- ✅ Relatórios e exportação
- ✅ Geração de executável (.exe)
- ✅ Arquivo único para gerenciar tudo (SISTEMA_ALS.bat)

---

**Desenvolvido para ALS** 🚛


