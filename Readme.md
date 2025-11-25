# 🚛 Sistema de Manutenção ALS

Sistema completo para gerenciamento de manutenção de veículos da frota ALS.

## 📦 Conteúdo do Sistema

### Banco de Dados (Já Pré-Carregado)
O sistema já vem com **141 veículos cadastrados**:
- 🚛 **39 Cavalos** (1 vazio)
- 🚚 **46 Carretas 1 Eixo**
- 🚚 **19 Carretas 2 Eixos** (5 vazias)
- 🐛 **21 Bugs** (diversos tipos)
- 🚗 **6 LS**
- ➕ Outros veículos

### Estrutura de Pastas
```
Sistema Manutenção ALS/
├── data/               # Banco de dados e arquivos de configuração
│   ├── sistema_als.db  # Banco SQLite com todos os veículos
│   └── ...
├── img/                # Imagens e logo
├── backup/             # Backups automáticos
├── output/             # Relatórios gerados
└── src/                # Código fonte do sistema
```

## 🚀 Como Gerar o Executável

1. **Execute o arquivo**: `GERAR_EXECUTAVEL.bat`
2. Aguarde a compilação (pode levar alguns minutos)
3. O executável estará em: `dist\SistemaManutencaoALS.exe`

## 💡 Uso do Sistema

### Primeiro Uso
- O sistema já vem com todos os veículos cadastrados
- Não é necessário importar nada
- Basta executar e começar a usar

### Adicionar Novos Veículos
- Use a opção de cadastro dentro do sistema
- Os veículos vazios já estão identificados com a descrição "VAZIO"

### Backup Automático
- O sistema faz backup automático do banco de dados
- Backups são salvos na pasta `backup/`

## 📋 Requisitos

- Windows 7 ou superior
- Python 3.8+ (apenas para desenvolvimento)
- O executável NÃO precisa de Python instalado

## 🔧 Desenvolvimento

### Instalar Dependências
```bash
pip install -r requirements.txt
```

### Executar em Modo Desenvolvimento
```bash
python src/main.py
```

## 📝 Notas Importantes

- ✅ Banco de dados já está populado com todos os veículos
- ✅ Cavalos vazios identificados
- ✅ Carretas 2 eixos vazias identificadas
- ✅ Sistema pronto para distribuição
- ✅ Não requer instalação adicional

## 👨‍💼 Para Distribuição

Copie apenas o arquivo executável (`SistemaManutencaoALS.exe`) para o usuário final.
O sistema já contém tudo que precisa internamente.

---

**Desenvolvido para ALS Transportes**
