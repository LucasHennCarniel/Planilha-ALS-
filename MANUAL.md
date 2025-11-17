# Manual do Usuário - Sistema de Controle de Manutenção de Frota ALS

## Índice
1. [Introdução](#introdução)
2. [Primeiros Passos](#primeiros-passos)
3. [Interface do Sistema](#interface-do-sistema)
4. [Operações Básicas](#operações-básicas)
5. [Busca e Filtros](#busca-e-filtros)
6. [Relatórios](#relatórios)
7. [Exportação de Dados](#exportação-de-dados)
8. [Dicas e Boas Práticas](#dicas-e-boas-práticas)

## Introdução

O Sistema de Controle de Manutenção de Frota ALS é uma aplicação standalone desenvolvida para facilitar o gerenciamento de manutenções de veículos. O sistema não necessita de internet e armazena todos os dados em uma planilha Excel local.

### Objetivos do Sistema
- Registrar todas as manutenções realizadas na frota
- Controlar custos de manutenção
- Acompanhar status das manutenções
- Planejar manutenções futuras baseadas em quilometragem
- Gerar relatórios e estatísticas

## Primeiros Passos

### 1. Instalação
Siga as instruções no arquivo README.md para instalar Python e as dependências necessárias.

### 2. Primeira Execução
Execute o comando:
```bash
python sistema_manutencao.py
```

Na primeira execução, o sistema criará automaticamente o arquivo `manutencao_frota.xlsx` vazio.

### 3. Interface Principal
Ao abrir o sistema, você verá três áreas principais:
- **Formulário de Cadastro** (topo)
- **Busca e Ações** (meio)
- **Tabela de Registros** (base)

## Interface do Sistema

### Formulário de Cadastro

#### Campos Obrigatórios (*)
- **Veículo***: Nome ou modelo do veículo (ex: "Caminhão Mercedes 1620")
- **Placa***: Placa do veículo (ex: "ABC-1234")

#### Campos Opcionais
- **Tipo**: Selecione o tipo de manutenção
  - Preventiva: Manutenção planejada
  - Corretiva: Reparo de problemas
  - Preditiva: Manutenção baseada em monitoramento
  - Revisão: Revisão programada
  - Outros: Outros tipos

- **Descrição**: Descreva o serviço realizado (ex: "Troca de óleo e filtros")

- **Custo (R$)**: Valor gasto na manutenção (apenas números)

- **KM Atual**: Quilometragem do veículo no momento da manutenção

- **Próximo KM**: Quilometragem estimada para próxima manutenção

- **Status**: Status atual da manutenção
  - Concluída: Manutenção finalizada
  - Pendente: Aguardando execução
  - Em Andamento: Sendo executada
  - Agendada: Programada para o futuro

- **Responsável**: Nome do responsável pela manutenção

- **Observações**: Informações adicionais relevantes

### Botões de Ação

- **Adicionar**: Cria um novo registro com os dados do formulário
- **Atualizar**: Atualiza o registro selecionado com os novos dados
- **Limpar**: Limpa todos os campos do formulário
- **Excluir**: Remove o registro selecionado (pede confirmação)

### Área de Busca

- **Buscar por**: Selecione o campo para busca
  - Veículo
  - Placa
  - Tipo_Manutencao
  - Status

- **Campo de Busca**: Digite o termo que deseja buscar

- **Buscar**: Executa a busca e filtra os registros

- **Mostrar Todos**: Remove os filtros e exibe todos os registros

### Botões de Ação Global

- **Relatório**: Gera estatísticas sobre as manutenções
- **Exportar**: Salva os dados em um novo arquivo Excel

### Tabela de Registros

Exibe todos os registros de manutenção com as seguintes colunas:
- ID, Data, Veículo, Placa, Tipo, Descrição, Custo, KM Atual, Próximo KM, Status, Responsável

**Dica**: Clique em qualquer linha para selecionar e carregar os dados no formulário.

## Operações Básicas

### Adicionar Nova Manutenção

1. Preencha pelo menos os campos obrigatórios (Veículo e Placa)
2. Preencha os demais campos conforme necessário
3. Clique em "Adicionar"
4. Uma mensagem de confirmação aparecerá
5. O registro será exibido na tabela automaticamente

**Exemplo**:
```
Veículo: Caminhão Volvo FH 540
Placa: DEF-5678
Tipo: Preventiva
Descrição: Troca de óleo do motor e filtros
Custo: 850.00
KM Atual: 120000
Próximo KM: 130000
Status: Concluída
Responsável: João Silva
Observações: Trocado também filtro de combustível
```

### Editar Manutenção Existente

1. **Selecione** o registro na tabela (clique na linha)
2. Os dados serão carregados automaticamente no formulário
3. **Modifique** os campos desejados
4. Clique em "Atualizar"
5. Confirme as alterações

**Importante**: O ID e a Data original não podem ser alterados.

### Excluir Manutenção

1. **Selecione** o registro na tabela
2. Clique em "Excluir"
3. **Confirme** a exclusão na janela de diálogo
4. O registro será removido permanentemente

**Atenção**: Esta ação não pode ser desfeita! Use a funcionalidade de exportação para fazer backups regulares.

### Limpar Formulário

- Clique em "Limpar" a qualquer momento para resetar todos os campos
- Use esta função antes de adicionar um novo registro para garantir que não há dados antigos

## Busca e Filtros

### Busca Simples

1. Selecione o **campo** no qual deseja buscar (Veículo, Placa, Tipo ou Status)
2. Digite o **termo** de busca
3. Clique em "Buscar"

**Exemplos**:
- Buscar por Veículo: "Mercedes" (encontra todos os Mercedes)
- Buscar por Status: "Pendente" (mostra manutenções pendentes)
- Buscar por Placa: "ABC" (encontra placas que contenham ABC)

### Busca Parcial

O sistema faz busca parcial, ou seja:
- Buscar "Caminhão" encontrará "Caminhão Mercedes 1620"
- Buscar "ABC" encontrará "ABC-1234" e "ABC-5678"
- A busca não diferencia maiúsculas de minúsculas

### Mostrar Todos os Registros

- Clique em "Mostrar Todos" para remover qualquer filtro
- Todos os registros serão exibidos novamente

## Relatórios

### Gerar Relatório

1. Clique no botão "Relatório"
2. Uma janela aparecerá com as seguintes informações:

**Estatísticas Gerais**:
- Total de registros cadastrados
- Custo total de todas as manutenções

**Distribuição por Status**:
- Quantidade de manutenções por cada status
- Útil para ver quantas estão pendentes ou em andamento

**Distribuição por Tipo**:
- Quantidade de manutenções por tipo
- Ajuda a entender o perfil das manutenções (preventivas vs corretivas)

### Exemplo de Relatório

```
=== RELATÓRIO DE MANUTENÇÕES ===

Total de Registros: 45
Custo Total: R$ 45,750.00

Por Status:
  - Concluída: 32
  - Pendente: 8
  - Em Andamento: 3
  - Agendada: 2

Por Tipo de Manutenção:
  - Preventiva: 25
  - Corretiva: 15
  - Revisão: 3
  - Preditiva: 2
```

## Exportação de Dados

### Como Exportar

1. Clique no botão "Exportar"
2. Escolha o **local** onde deseja salvar o arquivo
3. Digite o **nome** do arquivo
4. Clique em "Salvar"

### Uso da Exportação

**Backup Regular**:
- Recomendamos exportar os dados semanalmente
- Mantenha backups em local seguro

**Compartilhamento**:
- Exporte para compartilhar dados com outros departamentos
- O arquivo exportado pode ser aberto no Excel

**Análises Externas**:
- Use o arquivo exportado para análises em outras ferramentas
- Integre com sistemas de relatórios existentes

## Dicas e Boas Práticas

### Organização dos Dados

1. **Use nomenclatura consistente**
   - Veículos: "Tipo + Marca + Modelo" (ex: "Caminhão Mercedes 1620")
   - Placas: Sempre no formato "ABC-1234"

2. **Preencha todos os campos**
   - Mesmo os opcionais ajudam em análises futuras
   - Observações podem ser cruciais para histórico

3. **Mantenha status atualizados**
   - Atualize de "Agendada" para "Em Andamento" quando iniciar
   - Marque como "Concluída" assim que finalizar

### Controle de Quilometragem

1. **Registre KM Atual sempre**
   - Fundamental para planejamento de manutenções
   - Ajuda a identificar padrões

2. **Defina Próximo KM**
   - Baseie-se nas recomendações do fabricante
   - Use o histórico para ajustar intervalos

3. **Monitore regularmente**
   - Busque por "Próximo KM" próximos da quilometragem atual
   - Planeje manutenções com antecedência

### Controle Financeiro

1. **Registre todos os custos**
   - Inclua peças, mão de obra e outros gastos
   - Use formato numérico simples (ex: 1500.50)

2. **Gere relatórios mensais**
   - Acompanhe o custo total de manutenções
   - Identifique veículos com alto custo

3. **Analise tendências**
   - Compare custos preventivas vs corretivas
   - Veículos com muitas corretivas podem precisar substituição

### Segurança dos Dados

1. **Backups regulares**
   - Use a função "Exportar" semanalmente
   - Mantenha múltiplas cópias em locais diferentes

2. **Não edite o Excel diretamente**
   - Use sempre o sistema para garantir integridade
   - Edições manuais podem causar erros

3. **Feche o Excel antes de usar o sistema**
   - O arquivo não pode estar aberto em dois programas
   - Feche o Excel antes de executar o sistema

### Resolução de Problemas Comuns

**Problema**: Erro ao salvar dados
- **Solução**: Verifique se o arquivo Excel não está aberto

**Problema**: Registro não aparece na tabela
- **Solução**: Clique em "Mostrar Todos" para remover filtros

**Problema**: Não consigo atualizar um registro
- **Solução**: Selecione o registro na tabela antes de clicar em "Atualizar"

**Problema**: Perdi dados
- **Solução**: Restaure de um backup exportado anteriormente

### Suporte

Para problemas técnicos ou dúvidas:
1. Consulte o arquivo README.md
2. Verifique a seção de Solução de Problemas
3. Entre em contato com o suporte técnico

---

**Versão do Manual**: 1.0  
**Data**: Novembro 2025  
**Desenvolvedor**: Lucas Henn Carniel
