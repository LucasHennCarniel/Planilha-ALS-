# Sistema de Controle de Manutenção de Frota - ALS

## Descrição

Sistema standalone desenvolvido em Python para gerenciar manutenções da frota da ALS. A aplicação utiliza uma planilha Excel como base de dados e oferece interface gráfica com cadastro, edição, busca, relatórios, exportação e atualização automática da planilha.

**Características:**
- ✅ Interface gráfica intuitiva com Tkinter
- ✅ Base de dados em Excel (sem necessidade de internet)
- ✅ Manipulação de dados com Pandas
- ✅ Totalmente standalone (sem dependências externas complexas)
- ✅ Atualização automática da planilha
- ✅ Busca e filtragem avançada
- ✅ Relatórios estatísticos
- ✅ Exportação de dados

## Requisitos

- Python 3.7 ou superior
- Bibliotecas (instaladas via requirements.txt):
  - pandas==2.0.3
  - openpyxl==3.1.2

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/LucasHennCarniel/Planilha-ALS-.git
cd Planilha-ALS-
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Executar o Sistema

```bash
python sistema_manutencao.py
```

### Executar Demo (sem GUI)

Para ver uma demonstração do sistema funcionando sem interface gráfica:

```bash
python demo.py
```

Este script demonstra:
- Criação automática do banco de dados
- Adição de registros
- Busca e filtragem
- Atualização de registros
- Geração de estatísticas

### Criar Template Excel (Opcional)

Se desejar criar um arquivo Excel de exemplo com dados de demonstração:

```bash
python create_template.py
```

## Funcionalidades

### 1. Cadastro de Manutenção
- **Veículo**: Nome/modelo do veículo
- **Placa**: Placa do veículo
- **Tipo**: Preventiva, Corretiva, Preditiva, Revisão ou Outros
- **Descrição**: Detalhes do serviço realizado
- **Custo**: Valor da manutenção em reais
- **KM Atual**: Quilometragem no momento da manutenção
- **Próximo KM**: Quilometragem para próxima manutenção
- **Status**: Concluída, Pendente, Em Andamento ou Agendada
- **Responsável**: Nome do responsável pela manutenção
- **Observações**: Notas adicionais

### 2. Operações

#### Adicionar Registro
1. Preencha os campos do formulário
2. Clique em "Adicionar"
3. O registro será salvo automaticamente no Excel com ID único e data

#### Editar Registro
1. Selecione um registro na tabela (clique na linha)
2. Os dados serão carregados no formulário
3. Modifique os campos desejados
4. Clique em "Atualizar"

#### Excluir Registro
1. Selecione um registro na tabela
2. Clique em "Excluir"
3. Confirme a exclusão

#### Buscar Registros
1. Selecione o campo de busca (Veículo, Placa, Tipo ou Status)
2. Digite o termo de busca
3. Clique em "Buscar"
4. Use "Mostrar Todos" para ver todos os registros novamente

### 3. Relatórios

Clique em "Relatório" para visualizar estatísticas:
- Total de registros
- Custo total das manutenções
- Distribuição por status
- Distribuição por tipo de manutenção

### 4. Exportação

Clique em "Exportar" para salvar os dados em um novo arquivo Excel:
1. Escolha o local e nome do arquivo
2. Os dados serão exportados mantendo toda a estrutura

## Estrutura do Arquivo Excel

A planilha `manutencao_frota.xlsx` é criada automaticamente na primeira execução com as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| ID | Identificador único (gerado automaticamente) |
| Data | Data do registro (formato: DD/MM/AAAA) |
| Veiculo | Nome/modelo do veículo |
| Placa | Placa do veículo |
| Tipo_Manutencao | Tipo da manutenção |
| Descricao | Descrição do serviço |
| Custo | Custo em reais |
| KM_Atual | Quilometragem atual |
| Proximo_KM | Próxima manutenção em KM |
| Status | Status da manutenção |
| Responsavel | Responsável pela manutenção |
| Observacoes | Observações adicionais |

## Arquivos do Projeto

```
Planilha-ALS-/
├── sistema_manutencao.py       # Aplicação principal
├── create_template.py          # Gerador de template Excel
├── demo.py                     # Script de demonstração (sem GUI)
├── test_sistema.py             # Testes unitários
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
├── MANUAL.md                   # Manual do usuário
└── manutencao_frota.xlsx      # Base de dados (criado automaticamente)
```

## Características Técnicas

### Arquitetura
- **ExcelDatabase**: Classe responsável pela manipulação de dados Excel
  - Inicialização automática da base de dados
  - Operações CRUD (Create, Read, Update, Delete)
  - Sistema de busca integrado

- **MaintenanceApp**: Classe da interface gráfica
  - Interface Tkinter responsiva
  - Validação de campos obrigatórios
  - Atualização automática da tabela
  - Feedback visual para todas as operações

### Segurança e Confiabilidade
- Validação de campos obrigatórios
- Confirmação antes de exclusões
- Tratamento de erros com mensagens informativas
- IDs únicos gerados automaticamente
- Backup via exportação de dados

## Solução de Problemas

### Erro ao importar módulos
Certifique-se de que instalou as dependências:
```bash
pip install -r requirements.txt
```

### Arquivo Excel corrompido
1. Feche o arquivo Excel se estiver aberto
2. Faça backup do arquivo atual
3. Delete `manutencao_frota.xlsx`
4. Execute o sistema novamente para criar novo arquivo

### Erro de permissão
- Verifique se o arquivo Excel não está aberto em outro programa
- Certifique-se de ter permissões de escrita no diretório

## Desenvolvedor

Lucas Henn Carniel

## Licença

Este projeto foi desenvolvido para uso interno da ALS.
